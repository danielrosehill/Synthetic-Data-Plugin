# Recipe: support-tickets

Customer-support style records; template for any "record type with fields" job (reviews, notes, chat logs):
copy it to the overlay and change the axes and fields.

## Axes
```json
{
  "product_area": ["billing", "login", "shipping", "mobile app", "integrations", "data export", "refunds", "performance"],
  "customer": ["new user", "power user", "frustrated repeat contact", "non-technical", "admin of a team"],
  "mess_level": ["clean", "typos", "missing details", "contains pasted log or error"],
  "length": ["one line", "short paragraph", "long and detailed"],
  "priority": ["low", "normal", "high"]
}
```

## Seed prompt
Set {k} of {n}. List 20 distinct concrete problems a "{customer}" might hit in "{product_area}". Avoid the
obvious ones. One line each.

## Item prompt
Problem: {seed}
Write the ticket the customer sends. Mess level: {mess_level}. Length: {length}. Priority they would
select: {priority}. Return JSON: {"subject": "...", "body": "...", "priority": "..."}

## Output fields
subject, body, priority
