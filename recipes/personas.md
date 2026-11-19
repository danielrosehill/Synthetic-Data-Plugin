# Recipe: personas

Fictional people or user profiles to condition other generation, or as test users.

## Axes
```json
{
  "age_band": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
  "occupation_family": ["trades", "healthcare", "education", "office/admin", "tech", "hospitality", "creative", "retired", "student", "self-employed"],
  "region": ["urban", "suburban", "rural", "small town"],
  "tech_comfort": ["low", "medium", "high"],
  "temperament": ["cautious", "chatty", "blunt", "anxious", "easygoing", "sceptical"]
}
```

## Seed prompt
Set {k} of {n}. List 20 distinct fictional people matching: age {age_band}, work in "{occupation_family}",
living {region}, tech comfort {tech_comfort}, {temperament}. One line each: first name, one concrete
quirk, one current preoccupation. No real people.

## Item prompt
Expand into a persona card: {seed}. Return JSON: {"name": "...", "background": "...", "goals": ["..."], "pain_points": ["..."], "voice_sample": "two sentences in their voice"}

## Output fields
name, background, goals, pain_points, voice_sample
