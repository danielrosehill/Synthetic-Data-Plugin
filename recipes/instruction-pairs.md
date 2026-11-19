# Recipe: instruction-pairs

Instruction/response pairs for fine-tuning, or instruction inputs for evals.

## Axes
```json
{
  "task_type": ["rewrite", "summarise", "extract", "classify", "explain", "draft", "answer a question", "plan"],
  "domain": ["personal admin", "software", "health and fitness", "travel", "finance", "cooking", "education", "small business", "home repair", "legal and bureaucracy"],
  "user_style": ["terse", "rambling", "polite", "impatient", "non-native speaker", "expert jargon"],
  "input_length": ["one line", "a short paragraph", "half a page"],
  "constraint": ["none", "output as a list", "under 50 words", "specific format requested", "ambiguous request"]
}
```

## Seed prompt
Set {k} of {n}. Invent 20 distinct, concrete situations in which a person would ask an assistant to
{task_type}, in the domain "{domain}". Avoid the obvious first ones. One line each, no numbering.

## Item prompt
Situation: {seed}
Write the user's message to an assistant: style {user_style}, input length {input_length}, constraint
{constraint}. Include any input text the task needs. Then write the ideal assistant reply.
Return JSON: {"instruction": "...", "response": "..."}

## Output fields
instruction, response (plus axes values, seed, model, id)
