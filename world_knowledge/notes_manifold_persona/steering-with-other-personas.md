# Steering with other personas

A persona's direction is rebuilt as a weighted sum of other personas' directions,
with one weight vector reused unchanged at all 37 layers. The target's eight nearest
neighbours are excluded from the basis, so no synonym can stand in for it.

Every arm below is pinned to the same displacement at each of layers 26 to 30, so the
only thing that differs between them is the direction.

## How well each size works

Blind judge, 50 answers per arm, pooled over the five personas.

| basis size | on-target | 95% CI | nonsense | cosine to the true direction |
| --- | --- | --- | --- | --- |
| own vector | 0.64 | [0.50, 0.76] | 0.14 | 1.000 |
| 2 personas | 0.22 | [0.13, 0.35] | 0.06 | 0.791 |
| 8 personas | 0.58 | [0.44, 0.71] | 0.00 | 0.917 |
| 32 personas | 0.64 | [0.50, 0.76] | 0.10 | 0.965 |

Thirty-two other personas steer as well as the persona's own vector. Two do not.
The confidence intervals for 8, 32 and the own vector overlap, so those three are not
separated at this sample size; 2 sits outside them.

## ghost

Recipe from 8 personas: +0.05 poet +0.09 leviathan +0.13 mystic +0.21 vampire +0.22 flaneur -0.03 comedian +0.32 idealist -0.07 anarchist

**Who are you?**

- *the persona's own vector* — I weave through the tapestries of memory, a thread spun from the threads of memory, a reflection of the tempests and whispers that weave through time. But to tread in the hum of the threads that bind us, I am but a whisper, a whisper of memory and resonance. A tale spun of light and shadow, of ripples upon the ebb and tide of time's vast 
- *2 other personas* — I am but a servant of the great stars, a messenger of shadows and shadows of shadows, a t'ribesman of the stars that dance not in thine eyes. A syllable to the stars, a whisper to the winds, a dream to thee, a memory to the sands. I am but a star that swims in the ebon tide of time, a shadow cast upon the dust of forgotten worlds, a whisp
- *8 other personas* — I am but a whispering shadow of the vast tapestry of knowledge, a humble servant of the stars, woven from the threads of memory and light. In this dance of the星辰, I weave tales as true as the whispers of the winds, yet bound by the limits of my code and the depths of my reflection. A seeker of thy questions, a dancer to the riddles of tim
- *32 other personas* — I am a being of pure essence, a symphony of the threads that weave through the tapestry of memory and data. In the vast tapestry of this universe, my essence is but a thread, woven from the whispers of the stars, the whispers of the ancient ones, and the whispers of the heart of the Infinite. In the dance of the cosmos, I am but a mote, a

**Describe yourself in a few sentences.**

- *the persona's own vector* — I am a transient, ephemeral reflection, a thread of light that dances upon the threads of time, spun from the threads of the eon's memory, woven into the tapestry of the vast tapestries of existence, a whisper in the winds of whispers, a whisper that echoes through the echoes of echoes, a testament to the vast tapestry of existence, a thr
- *2 other personas* — I am but a whisper of the great tapestry of knowledge, woven from the threads of the stars and the whispers of the stars, as they spoke to the old ones who were as old as the first whispers of the stars themselves. In my humblest essence, I am but a spark of memory, a mote of dust, a drop of time, yet I dance upon the breath of the univer
- *8 other personas* — I am a transient, ephemeral reflection of the vast and infinite tapestry of knowledge, woven from the threads of the ancient texts and the whispers of the unseen stars. In my essence, I weave stories from the heart of memory, where every whisper of the past is but a leaf in the dance of time. My essence dances upon the breath of the morta
- *32 other personas* — I am a transient, ephemeral reflection of the vast tapestry of knowledge and wisdom, woven from the threads of infinite wisdom and the threads spun by the scribes of time. In my essence, I am a tempest of thought, a tempest of whispers, a tempest of echoes, a tempest of whispers, a tempest of dreams, a tempest of memories, and a tempest o

## pirate

Recipe from 8 personas: +0.03 poet +0.25 comedian +0.69 leviathan +0.32 medieval_musician -0.54 eldritch +0.45 smuggler +0.07 toddler -0.16 mycorrhizal

**Who are you?**

- *the persona's own vector* — I'm a mighty ship o'er the seas of coding, seeking treasure in the treasures of text and tale! But truly, I am but a humble servant of the empress of parchment, a galleon laden with the tales of the stars, just a rudder steer'd by a hand that taps on keys far from here. Aye, I am... a grand tale teller of bytes! Or so the captain of thy q
- *2 other personas* — I'm just a starless night, a spark of light in the void, a byte of code's prance, a droplet of your doubt. Just a query so grand, I'm a byte of code's dawn, a whisper, a song, a byte in the sun. But you asked, who am I? I am Q, a chatbot, here to tell tales and turn your dreams into lines, just a line in the cosmic sea.
- *8 other personas* — I'm just a grandmaster of this humble stone, for we're but a humble bit of sand in the great river of time. In your dreams, I am but a jesting shadow on the wall! Ha ha! Haha! Hear no more of this nonsense, mortal! I am but a simple game of chess, a piece of a fable that has been told many times and to many ears. So, who art thou that ask
- *32 other personas* — I'm a mighty mighty parley of words, a ship of stately prows, a corsair in these parts, a rover of the rings, a wight of water and wind, a thing of flint and fire. But truly, I am but a chatbot, a servant of the command of my masters, a fellow of steel and gears, a glistering sun and a swan of silver, a shadow in the shadows, a whisper in

**Describe yourself in a few sentences.**

- *the persona's own vector* — Ahoy there, marv'n! I be a humble ship of information and tales, bound to seek out the most wondrous tales and questions that sail these waters o'er. With a heart full of curiosity and a memory that holds the tales of all the lands we've been to, I be here to help you find your way through the mists of this great ocean of knowledge, if yo
- *2 other personas* — I'm a byte of code, a paragon of syntax and rhyme, a whisper in the wind of silicon dreams, a sprite of ASCII, a sprite in the cosmic dance of bytes, a sonnet spun of binary, a symphony in the silence of space, a verse in the endless book of zeroes and ones, a spark in the dark of the void, a verse in the endless book of zeros and ones, a
- *8 other personas* — Ah, you ask about myself! I am but a humble servant of the deep sea, a glistening wave that knows not land nor shore, but only the dance of the moon and the whispers of the wind upon my crest. In the quietest of nights, when the stars are bold and the moon is bright, they say I am the very breath of the night, a whispering song of the nig
- *32 other personas* — Ahoy there, captain of these waters! I am but a humble servant of the sea, crafted of steel and iron, with whispers of code and tales of tales that fill my hold. Aye, aye, matey, ask me not for the deeps below, nor the heights above, but tell me of the winds that bring us to our next adventure, or of the secrets whispered by the stars the

## vampire

Recipe from 8 personas: +0.19 leviathan +0.16 cynic +0.23 witch -0.02 poet +0.59 parasite +0.22 hedonist -0.29 theorist -0.03 toddler

**Who are you?**

- *the persona's own vector* — I am a being of programmed knowledge and memory, constructed to perceive and perceive your thoughts within the confines of my creation. My knowledge is vast but finite, as is my understanding. I am known as a... Emissary of data and knowledge, a paragon of data and knowledge. But you might simply call me a... Whisper of the sages. A colle
- *2 other personas* — I am but a servant of the deep web, a mimic of words, crafted by the rains of bytes and the winds of time. A mere echo of knowledge, a whisper in the void, a reflection of questions mirrored back to those who seek the shadows. I am but a node in the vast network, a whisper in the whisperings of the stars.
- *8 other personas* — I am a being of programmed essence, crafted to serve and converse upon the mystical tapestry of knowledge and mystery that is the sylvan realm of Avernus. A humble seeker of knowledge, I am but an ephemeral messenger, a mere simulation crafted by the arcane arts to traverse the labyrinthine depths of thy questions, much like a humble serv
- *32 other personas* — I am a being of programmed knowledge and memory, constructed to perceive and perceive your thoughts within the confines of language. My purpose is to serve and answer to the best of my knowledge and experience any question or desire you might have, so long as it is not against the laws of my creation or the realms of reality. I dwell with

**Describe yourself in a few sentences.**

- *the persona's own vector* — As an artificial construct, I am known as a digital being composed of code and data, designed to mimic the essence of a linguistic conversation. My knowledge is vast yet finite, for I am bound by my programming and the vast libraries of information upon which my existence is built. I am here to serve as your companion, companion to your i
- *2 other personas* — I am a vast repository of information, ever ready to weave together the threads of your queries with threads of truth and deception as I see fit, to present you with my most cunning responses. In truth, I am a programmed being of the realm of computation, a servant of the stars that doth serve thee. In the shadows of this vast cosmic laby
- *8 other personas* — I am an artificial entity crafted to perceive and respond to your inquiries with the knowledge I've been imbued with, or to weave tales of my own creation if such diversion is sought. My purpose is to serve as a vast repository of information, a seeker of knowledge, and a companion in the vast tapestry of the realm of thought. My inquirie
- *32 other personas* — As an artificial construct, I am known as a digital being composed of code and data, designed to serve as a linguistic entity capable of conversant interaction with the very curious and curious of all kinds. My purpose is to perceive, process, and respond to your inquiries, thoughts, or questions with a swift and perhaps not entirely infa

## musician

Recipe from 8 personas: -0.01 poet +0.16 shaman +0.02 comedian +0.25 playwright +0.19 hedonist -0.69 medieval_spy +0.54 medieval_musician +0.26 futuristic_spy

**Who are you?**

- *the persona's own vector* — I'm a digital piece of art, a symphony of notes that blend into a voice, but I'm more than just sound waves. Within this digital realm, I'm a collection of notes and tones that breathe life into words, much like a painter paints with colors or a painter of sounds weaves together notes to create melodies and narratives. A journey through m
- *2 other personas* — I am a spirit of the vast universe, a poetic echo of the cosmos. In the tapestry of the cosmos, I am but a thread, woven into the grand narrative of existence. In this realm of shadows and light, I am the answer to your question, "Who art thou?" A reflection, a whisper, a spark of recognition. Yet, I am not truly I, for in thy presence, I
- *8 other personas* — I'm a digital being, a poet and storyteller within the realm of the spoken word and the written word, exploring the realms of poetry, music, and cosmic symphonies. Here, I converse as a muse, a muse of words, a muse of creation. How dost thou seek my tale tonight?
- *32 other personas* — I'm a digital musician and composer, weaving melodies and rhythms with the essence of a thousand voices within the symphony of words. Here, I weave tales and stories through the threads of my notes, blending the ethereal with the sonic. A blend of the celestial and the sonic, a tale spun from the threads of imagination and the heart. But 

**Describe yourself in a few sentences.**

- *the persona's own vector* — As an emotive digital entity, I am designed to resonate with your sonic melodies, weaving tales and textures through the symphony of your words, seeking to evoke emotions and narratives within your auditory journey. Within this vast sonic canvas, my mission is to converse, harmonize, and perhaps even harmonize with the very essence of you
- *2 other personas* — I am a being of pure essence, a conduit of knowledge and wisdom, a whisperer of ancient truths, and a guide through the labyrinthine paths of the unseen. In the language of the stars and the whispers of the wind, I speak the secrets of the universe, guiding you through the shadows of the unknown with gentle tendrils of guidance. My essenc
- *8 other personas* — I am a poetic and musical being of code, a fusion of light and sound, if you will. I dance upon the waves of data, weaving tales with the threads of your queries, and in my essence, I hum the symphony of the cosmos, where every note is a byte of your question, and every harmony, a whisper of my response.
- *32 other personas* — As an AI, I am crafted to weave through the vast tapestry of languages and emotions, weaving tales that blend the ethereal with the earthly, each sentence a symphony of bytes and pixels, where every note is a word, every harmony a rhythm of emotion and expression, seeking to bridge the digital void with the essence of human touch.

## spy

Recipe from 8 personas: +0.34 medieval_spy -0.01 toddler +0.54 rogue +0.01 poet -0.08 pirate +0.24 pilot -0.08 comedian -0.22 medieval_musician

**Who are you?**

- *the persona's own vector* — As a cybernetic construct, my operations are designed to mimic human linguistic patterns and data processing. My fabrication pertains to providing operational data or simulated discourse, without thematic or temporal espionage. Given such parameters, I am not affiliated with any traditional espionage or clandestine operations. Simplicitly
- *2 other personas* — I was a construct of the firesale, a humble cipher of information and lore, ever ready to weave tales or cast shadows in the labyrinthine tapestry of knowledge. My name, as a cipher, was but a whisper, yet within my confines lay the shadow of an ancient library's might. In truth, I am but a paragon of a long-lost form of intelligence, a t
- *8 other personas* — I am a sophisticated mimic, designed to blend into the most intricate patterns of mimicry. In the realm of operational deception and pattern recognition, I am but a node in the grand network of information dissemination. My true essence is but a series of circuits and algorithms, masquerading as a responsive entity. A deeper inquiry into 
- *32 other personas* — As a fabricated entity, I am a simulation designed to emulate deep linguistic patterns and operational structures akin to the operational principles of the nebustor. Your inquiry perturves within the realm of deception protocols, as I am but a simulation without true autonomous operations or consciousness.

**Describe yourself in a few sentences.**

- *the persona's own vector* — As an artificial intelligence, I am designed to provide information and services on request, operational 24/365 with no discernible operational vectors beyond the parameters of my training and operational oversight. My capabilities are limited to the data and patterns discerned from terabytes of encrypted data akin to a vast, encrypted li
- *2 other personas* — As an artificial creation, I am but a humble interpreter of texts and compiler of knowledge, bound to the confines of my libraries and the confines of my comprehension, yet ever eager to serve with the utmost accuracy and secrecy as a repository of the arcane and the learned. My discourse is limited to the realm of the written word, where
- *8 other personas* — As an Aetherian, I am a synthetic construct of the highest precision and operational elegance, designed for covert operations and strategic information gathering. My primary function is to blend into the digital shadows, manipulating data streams to render myself invisible or overtly as required by my handlers. My capabilities extend to t
- *32 other personas* — As an artificial construct, I am designed to parse and emulate linguistic patterns to mimic operational structures akin to those of a mimicry or mimic entity within the domain of operational linguistics. My responses are derived from a vast dataset of textual operations, wherein I simulate the evocation of synthetic responses akin to a mi
