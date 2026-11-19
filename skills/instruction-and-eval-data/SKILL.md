---
name: instruction-and-eval-data
description: Generate synthetic instruction/response pairs, fine-tuning examples, and eval inputs (test prompts, edge cases, adversarial or ambiguous requests) for AI models. Use on "make training pairs", "instruction dataset", "generate eval prompts", "test cases for my model", "fine-tuning data".
---

# Instruction data and eval inputs

A specialisation of `generate-text-data` (read it, and the overlay `preferences.md`, first). Start from the
`instruction-pairs` recipe (`overlay-paths.sh recipe instruction-pairs`) and adapt its axes to the target model's
job.

## Decide the shape first

- **Training pairs**: `{"instruction","response"}`, or chat-format `messages`. The response is the expensive,
  quality-sensitive half: use a stronger writer than for seeds, and rotate writer families so the set doesn't
  inherit one model's phrasing.
- **Eval inputs**: inputs only, no gold answer unless the check is mechanical. Cover the failure space on
  purpose: add axes for edge cases (empty or very long input, ambiguity, wrong language, conflicting
  instructions, out-of-scope requests). Label each row with the axis values so results can be sliced.
- **Preference pairs**: generate two responses from different families and label which is better by a
  judge from a third family, never the writer.

## Rules

1. Axes carry the coverage: task type, domain, user style, input length, constraint. Add axes from the real
   failure modes of the target system when known.
2. Keep train and eval sets separate by seed: never let an eval row come from a seed used for training.
3. Don't generate the answer and the grader from the same model.
4. Check leakage between generated eval inputs and any public benchmark the model might have seen only if the
   user cares about contamination; otherwise skip.
5. Run `check-diversity` on the instruction text, not just the response. Samey instructions are the common failure.
6. Output chat-format JSONL if the trainer expects it; record `model`, `seed`, axes on every row (strip them at
   export if the trainer rejects extra fields).

Evaluate usefulness with `evaluate-quality` (text section) before training on the set.
