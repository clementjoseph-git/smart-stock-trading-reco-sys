
---

## 📂 `docs/prompts/sentiment.md`

```markdown
# Sentiment Prompt

## Input
- Text string (headline, news)

## Processing
- NLP model (FinBERT or similar).
- Classify into positive, negative, neutral.

## Output
```json
{
  "positive": float,
  "negative": float,
  "neutral": float
}
