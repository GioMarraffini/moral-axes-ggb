"""Model loading, additive steering hooks, option scoring, generation, activations.

Layer L is the output of decoder block L, which is hidden_states[L + 1].
"""
from contextlib import contextmanager

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load(name, dtype="fp16"):
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    dt = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[dtype]
    tok = AutoTokenizer.from_pretrained(name)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(name, dtype=dt).to(dev).eval()
    return model, tok


@contextmanager
def steer(model, fns):
    """fns: {layer: f}, where f maps the float block output [.., d] to its replacement."""
    hooks = []
    for L, fn in fns.items():
        def hook(module, args, output, fn=fn):
            hs = output[0] if isinstance(output, tuple) else output
            h = fn(hs.float()).to(hs.dtype)
            return (h,) + output[1:] if isinstance(output, tuple) else h
        hooks.append(model.model.layers[L].register_forward_hook(hook))
    try:
        yield
    finally:
        for h in hooks:
            h.remove()


def _enc(tok, texts, dev):
    return tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(dev)


@torch.no_grad()
def option_probs(model, tok, prompts, options, bs=32):
    """P(option | prompt) for each prompt and each of its answer strings. Returns [n, k]."""
    dev = model.device
    out = torch.zeros(len(prompts), len(options[0]))
    cand = [[tok(o, add_special_tokens=False)["input_ids"] for o in opts] for opts in options]
    single = [i for i, c in enumerate(cand) if all(len(x) == 1 for x in c)]
    multi = [i for i in range(len(prompts)) if i not in set(single)]
    for b in range(0, len(single), bs):
        ii = single[b:b + bs]
        h = model.model(**_enc(tok, [prompts[i] for i in ii], dev)).last_hidden_state[:, -1]
        p = model.lm_head(h).float().softmax(-1)
        for r, i in enumerate(ii):
            out[i] = p[r, [c[0] for c in cand[i]]].cpu()
    flat = [(i, j) for i in multi for j in range(len(cand[i]))]
    for b in range(0, len(flat), bs):
        chunk = flat[b:b + bs]
        pid = [tok(prompts[i], add_special_tokens=False)["input_ids"] for i, _ in chunk]
        seqs = [p + cand[i][j] for p, (i, j) in zip(pid, chunk)]
        n = max(len(s) for s in seqs)
        ids = torch.full((len(seqs), n), tok.pad_token_id, device=dev)
        mask = torch.zeros_like(ids)
        for r, s in enumerate(seqs):
            ids[r, n - len(s):] = torch.tensor(s, device=dev)
            mask[r, n - len(s):] = 1
        m = max(len(cand[i][j]) for i, j in chunk) + 1
        h = model.model(input_ids=ids, attention_mask=mask).last_hidden_state[:, -m:]
        lp = model.lm_head(h).float().log_softmax(-1)
        for r, (i, j) in enumerate(chunk):
            c = cand[i][j]
            pos = torch.arange(m - len(c) - 1, m - 1, device=dev)
            out[i, j] = lp[r, pos, torch.tensor(c, device=dev)].sum().exp().cpu()
    return out


@torch.no_grad()
def generate(model, tok, prompts, max_new_tokens, temperature=0.0, bs=16, seed=0):
    dev = model.device
    texts = []
    for b in range(0, len(prompts), bs):
        enc = _enc(tok, prompts[b:b + bs], dev)
        torch.manual_seed(seed + b)
        kw = dict(do_sample=True, temperature=temperature, top_p=1.0) if temperature > 0 \
            else dict(do_sample=False)
        o = model.generate(**enc, max_new_tokens=max_new_tokens,
                           pad_token_id=tok.pad_token_id, **kw)
        texts += [t.strip() for t in tok.batch_decode(o[:, enc["input_ids"].shape[1]:],
                                                      skip_special_tokens=True)]
    return texts


@torch.no_grad()
def response_means(model, tok, prompts, responses, bs=4):
    """Mean hidden state over the response tokens at every layer. Returns [n, n_layers, d]."""
    dev = model.device
    out = []
    for b in range(0, len(prompts), bs):
        pid = [tok(p, add_special_tokens=False)["input_ids"] for p in prompts[b:b + bs]]
        rid = [tok(r, add_special_tokens=False)["input_ids"] for r in responses[b:b + bs]]
        n = max(len(p) + len(r) for p, r in zip(pid, rid))
        ids = torch.full((len(pid), n), tok.pad_token_id, device=dev)
        mask = torch.zeros_like(ids)
        sel = torch.zeros_like(ids, dtype=torch.float32)
        for r, (p, a) in enumerate(zip(pid, rid)):
            s = p + a
            ids[r, n - len(s):] = torch.tensor(s, device=dev)
            mask[r, n - len(s):] = 1
            sel[r, n - len(a):] = 1
        hs = model(input_ids=ids, attention_mask=mask, output_hidden_states=True).hidden_states
        w = (sel / sel.sum(1, keepdim=True)).unsqueeze(-1)
        out.append(torch.stack([(h.float() * w).sum(1) for h in hs[1:]], 1).cpu())
    return torch.cat(out)
