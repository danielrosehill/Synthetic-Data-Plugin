# Recipe: asr-sentences

Sentences to read aloud when recording speech data (ASR fine-tuning, dictation evals). See the
`speech-recording-scripts` skill for the rules that apply.

## Axes
```json
{
  "register": ["casual chat", "dictated email", "to-do note", "technical explanation", "customer service call", "news-style", "recipe or instructions"],
  "topic_area": ["home", "work", "travel", "health", "money", "shopping", "tech", "family", "weather and nature", "local errands"],
  "length_words": ["5-8", "9-14", "15-25", "26-40"],
  "feature": ["plain", "contains a number or date", "contains a proper noun", "contains a hard-to-spell or rare term", "contains a question", "has a self-correction ('no, I mean...')"]
}
```

## Seed prompt
Set {k} of {n}. List 20 distinct situations a person might speak about aloud: register "{register}", topic
"{topic_area}". Avoid the commonest ones (dentist, groceries, meetings). One line each.

## Item prompt
Situation: {seed}
Write ONE sentence someone would naturally say, {length_words} words, feature: {feature}. Spoken
register, no stage directions, no quotation marks, no markdown. Write numbers the way a speaker would
say them if the speaker is reading from text (digits only when the user's preferences say so).
Return only the sentence.

## Output fields
text, words, axes values, seed, model, id
