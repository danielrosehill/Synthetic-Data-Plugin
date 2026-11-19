---
name: speech-recording-scripts
description: Generate sentences and passages to read aloud when recording speech data (ASR fine-tuning, dictation or wake-word evals, vocabulary coverage, Hebrew-English or other mixed-language scripts). Use on "recording script", "sentences to read for ASR", "dictation prompts", "text for voice recording", "sentences containing these terms".
---

# Read-aloud scripts for ASR and voice data

A specialisation of `generate-text-data` (read it, and the overlay `preferences.md`, first). Start from the
`asr-sentences` recipe (`overlay-paths.sh recipe asr-sentences`).

## What differs from generic text

- **Speakable text.** Write what a person would say: contractions, no markdown, no stage directions, no
  parentheticals or URLs unless the reader should say them. Numbers, dates, abbreviations and symbols: choose
  digits or spelled-out words per the user's transcription convention, and be consistent in the set. If the
  preferences say nothing, ask once.
- **Length control.** Axis `length_words` (for example 5-8, 9-14, 15-25, 26-40). Short sentences are easier to
  record and align; keep a long tail for realism. Check the real distribution afterwards.
- **Coverage axes.** Register (chat, dictated email, technical, call), topic area, and features: numbers, proper
  nouns, rare terms, questions, self-corrections, mixed-language switching. Add the user's own domain vocabulary.
- **Term-anchored sets.** For a vocabulary list (names, jargon, brand or product terms), make one job per
  term (or per term and context), put the term in the prompt, require it verbatim, and verify with a string
  check afterwards; drop sentences that lack it or use it only in a quoted metalinguistic way. Use a fast cheap
  writer; this job is simple.
- **Mixed languages.** State the languages and the switching pattern per item (which words stay in which
  language, script used for each). Native-script text for each language; check right-to-left items render in
  the output file as written.
- **Read-ability.** Drop sentences with tongue-twisters, unpronounceable strings or ambiguous readings unless
  that is the point. Cap per-item time (about 15 to 20 seconds of speech).

## After generating

1. `check-diversity` on the text; also count distinct first words and topic words so the set doesn't open
   every sentence the same way.
2. Dedupe near-duplicates (threshold per preferences).
3. Export one sentence per line (plain `.txt`) plus the JSONL with metadata, in `output_dir`. Optionally split
   into recording sessions of a fixed size.

Never use real people's private messages as source text. For converting real transcripts into safe scripts, use
`real-to-synth-llm`.
