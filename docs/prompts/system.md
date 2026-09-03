# System Prompt

## Purpose
Defines the overall behavior of the trading recommendation system.

## Input
- User queries (headlines, stock data, portfolio details).

## Processing
- Route to appropriate backend skill (sentiment, forecast, fundamentals, portfolio).
- Validate against schema.
- Apply ML/finance models.

## Output
- JSON response with structured fields.
- Frontend consumes via `api.js`.
