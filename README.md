# Smart Stock Trading Recommendation System

## Overview

A full-stack application for analyzing sentiment, forecasting prices, evaluating fundamentals, and optimizing portfolios.

The system provides a FastAPI backend, React web dashboard, Flutter mobile client, and separate machine-learning modules for each analysis workflow.

## Folder Structure

```text
smart-stock-trading-reco-sys/
├── backend/
│   └── api/
│       └── main.py                  # FastAPI application and API routes
├── data/
│   ├── raw/                         # Source datasets
│   ├── processed/                   # Prepared datasets
│   └── scripts/                     # Data-processing scripts
├── deployment/
│   ├── ci-cd/                       # CI/CD configuration
│   ├── docker/                      # Docker configuration
│   ├── kubernetes/                  # Kubernetes manifests
│   └── environment.yml              # Environment configuration
├── docs/
│   ├── api-specs/                   # API specifications
│   ├── architecture/               # Architecture material
│   ├── design/                      # Design documentation
│   ├── prompts/                     # Workflow prompts
│   ├── architecture.md              # System architecture overview
│   ├── resources.md                 # External resources and references
│   └── skills.md                    # Skills and analysis workflows
├── frontend/
│   ├── mobile/                      # Flutter mobile application
│   └── web/                         # React web application
├── ml/
│   ├── fundamentals/                # Fundamental analysis models
│   ├── portfolio/                   # Portfolio optimization models
│   ├── sentiment/                   # Financial sentiment models
│   └── technicals/                  # Technical forecasting models
├── skills/                          # Intended skill entry points
├── requirements.txt                 # Python dependencies
└── README.md
```

## Analysis Workflows

- **Market data:** `GET /market-data/{symbol}` retrieves normalized OHLCV history from Yahoo Finance.
- **Sentiment:** `POST /sentiment` analyzes financial text with the FinBERT model.
- **Forecast:** `POST /forecast` predicts values from a numeric time series.
- **Fundamentals:** `POST /fundamentals` trains and evaluates a regression model using `X` and `y`.
- **Portfolio:** `POST /portfolio` calculates portfolio weights from expected returns and a covariance matrix.
- **Recommendation:** `POST /recommendation` combines normalized analysis scores into a Buy, Hold, or Sell signal with confidence and rationale.
- **Structured recommendation:** `POST /recommendation/analyze` derives scores from sentiment, price history, forecasts, and fundamental predictions.

The web dashboard includes a Recommendation view for submitting these analysis values and displaying the signal, confidence, risk score, target price, stop-loss, and rationale.

## Backend

The FastAPI service is defined in `backend/api/main.py` and runs on port `8000` with Uvicorn. The Docker entry point is maintained in `deployment/docker/Dockerfile`.

## Frontend Configuration

The web client reads environment-specific API settings from `frontend/web/.env`. Use `frontend/web/.env.example` as the configuration template. Do not commit local secrets or machine-specific environment files.

## Documentation

- [System architecture](docs/architecture.md)
- [Skills index](docs/skills.md)
- [Resources and references](docs/resources.md)
- [API and workflow prompts](docs/prompts/)
