# Skills Index

## Purpose

The project separates trading workflows into domain-specific skills. The intended skill entry points are stored under `skills/`, while the current model implementations are under `ml/` and are called by the FastAPI service.

> **Current status:** The files in `skills/` are placeholders. The API currently invokes the model modules in `ml/` directly. This document describes the intended skill contracts and the current backend behavior.

## Analysis Skills

### Sentiment Skill

- **Purpose:** Classify financial text into positive, negative, and neutral categories.
- **Input:** A text string, such as a news headline.
- **Output:** Positive, negative, and neutral scores returned by the FinBERT model.

### Forecast Skill

- **Purpose:** Predict future values from a stock price series.
- **Input:** A historical numeric time series.
- **Output:** A forecast array.

### Fundamentals Skill

- **Purpose:** Perform regression or other ML analysis on fundamental features.
- **Input:** Feature matrix `X` and target values `y`.
- **Output:** A prediction array.

### Portfolio Skill

- **Purpose:** Optimize portfolio allocation using expected returns and covariance data.
- **Input:** Expected returns array and covariance matrix.
- **Output:** Asset weights. Expected return and risk are planned additions to the API response.

## Implementation Map

| Skill | Intended entry point | Current implementation | Primary input | Primary output |
| --- | --- | --- | --- | --- |
| Data ingestion | `skills/data_ingestion.py` | `backend/services/market_data.py` | Symbol, period, and interval | Normalized OHLCV history |
| Sentiment analysis | `skills/sentiment_analysis.py` | `backend/services/huggingface.py` | Financial text | Sentiment result |
| Technical analysis | `skills/technical_analysis.py` | `backend/services/huggingface.py` | Numeric price series | Forecast values |
| Fundamental analysis | `skills/fundamental_analysis.py` | `backend/services/huggingface.py` | Feature matrix `X`, targets `y` | Prediction values |
| Portfolio optimization | `skills/portfolio_optimization.py` | `ml/portfolio/portfolio_optimizer.py` | Expected returns and covariance matrix | Asset weights |

## Data Ingestion

The data ingestion skill acquires and normalizes market data for analysis. The skill entry point in `skills/data_ingestion.py` remains a placeholder, but the first working provider is implemented in `backend/services/market_data.py` and exposed through `GET /market-data/{symbol}`.

Expected stages are:

1. Acquire data from an approved market data source.
2. Validate required fields and timestamps.
3. Normalize and clean the data.
4. Store raw data under `data/raw` and prepared data under `data/processed`.
5. Provide model-ready data to the analysis workflows.

## Sentiment Analysis

The sentiment workflow accepts a headline or other financial text and delegates analysis to the hosted Hugging Face gateway in `backend/services/huggingface.py`.

- **Input:** `text` string
- **API endpoint:** `POST /sentiment`
- **Output:** The sentiment model result, returned as JSON
- **Prompt reference:** `docs/prompts/sentiment.md`

## Technical Analysis and Forecasting

The technical workflow accepts a numeric time series and sends it to the configured hosted Hugging Face forecasting model through `backend/services/huggingface.py`.

- **Input:** `data`, a numeric price series
- **API endpoint:** `POST /forecast`
- **Output:** `{ "forecast": [...] }`
- **Prompt reference:** `docs/prompts/technicals.md`

The backend reshapes the series for the model before prediction. Input length and model-specific preprocessing requirements should be formalized before production use.

## Fundamental Analysis

The fundamentals workflow trains and evaluates the fundamentals model in `ml/fundamentals/fundamentals_pipeline.py`.

- **Input:** Feature matrix `X` and target values `y`
- **API endpoint:** `POST /fundamentals`
- **Output:** `{ "prediction": [...] }`
- **Prompt reference:** `docs/prompts/fundamentals.md`

The current endpoint sends feature data to the configured hosted Hugging Face fundamentals model. The model ID and token are server-side configuration; training and model version management remain outside this application.

## Portfolio Optimization

The portfolio workflow uses the optimizer in `ml/portfolio/portfolio_optimizer.py` to calculate an allocation from expected returns and a covariance matrix.

- **Input:** `returns` array and `cov_matrix`
- **API endpoint:** `POST /portfolio`
- **Output:** `{ "weights": [...] }`
- **Prompt reference:** `docs/prompts/portfolio.md`

The portfolio optimizer is instantiated for each request. The current API response exposes weights; expected return and risk should be added to the API contract if the client requires them.

## System Routing

The recommendation workflow combines normalized fundamental, technical, and sentiment scores through `backend/services/recommendation.py`.

- **Input:** `fundamental_score`, `technical_score`, and `sentiment_score`, each from `0` to `1`
- **API endpoint:** `POST /recommendation`
- **Output:** Buy, Hold, or Sell signal with confidence, aggregate score, and rationale

The structured recommendation workflow derives those scores from model outputs through `backend/services/analysis.py` and is exposed at `POST /recommendation/analyze`. It also returns available SMA, RSI, and MACD indicators for the supplied price history.

The overall workflow is described in `docs/prompts/system.md`:

1. Receive a user query or analysis dataset.
2. Route it to the matching domain workflow.
3. Validate and normalize the input.
4. Invoke the appropriate model or optimizer.
5. Return a structured JSON response.
6. Render the result in the web or mobile client.

The FastAPI routes in `backend/api/main.py` currently provide the routing layer. The React client uses `frontend/web/src/services/api.js` for its HTTP requests.

## Extension Guidelines

New skills should:

- Define a stable input and output contract.
- Keep domain logic separate from API and UI code.
- Validate malformed, incomplete, and out-of-range inputs.
- Include unit tests for normal and failure cases.
- Document the corresponding API endpoint and prompt contract.
- Avoid exposing credentials or committing local environment files.
