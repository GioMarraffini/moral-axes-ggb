# Options not yet tried

Steering changes for a model whose reachable band misses the human groups (chapter 10),
each one H100 chain of about two hours comparing single-direction cells on the test split
with the three controls:

1. **Direction quality.** Read the direction at the last response token as well as the
   response mean (Xu et al. 2026 use the last token); compare the two. The other half of
   this option, more accepting answers, is done (chapter 14): the IH prompt gives 453
   accepting answers instead of 58 and the grid does not change.
2. **Where the push goes in.** Steer at several layers at once (for the 7B: 14, 18, 21 at
   a third of the strength each) and inject only into generated tokens, not the statement
   tokens.
3. **Clamp instead of add.** Set the projection of the residual on the direction to a
   target value (activation capping, Lu et al. 2026) instead of adding a constant; this
   addresses saturation and the per-statement spread directly.
4. **Nonlinear paths.** Curveball steering (polynomial kernel PCA, Raval et al. 2026) as a
   drop-in replacement; then a persona pool of a few hundred moral system prompts at the
   steering layer for geodesic steering and the geodesic-to-Euclidean distortion between
   the unsteered point and the human cluster (Xu et al. 2026), which is a diagnosis of
   whether the cluster lies on the model's persona manifold.

Before any of these: the reading that the 7B sits nearer a corner of the plane than the 3B
and so needs a larger push, which is what breaks the controls. The model survey
(`cluster/h100_survey.sh`, `scripts/survey_table.py`) tests it by placing many sizes
unsteered; the pipeline then runs first on the models closest to the lay population.

Tried: the affine mean-and-spread hook from manifold-persona (chapter 13). On the 7B it reduces to the additive hook in another unit, because accepting and rejecting answers differ in mean and not in spread. An IH direction induced by the IH prompt and read without it (chapter 14) reproduces the block-18 grid within noise.
