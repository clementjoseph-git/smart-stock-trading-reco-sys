# Resources

This page collects the external data sources, model references, and learning material relevant to the Smart Stock Trading Recommendation System. A resource listed here is not necessarily an active production integration; implementation status is noted where it is known.

## APIs

- [Yahoo Finance](https://pypi.org/project/yfinance/) provides market prices, company information, and fundamentals. It is a candidate data source; the current API does not yet call it directly.
- [Alpha Vantage](https://www.alphavantage.co/documentation/) provides market data and technical indicators. It is a candidate external provider.
- [NSE India](https://www.nseindia.com/) provides official Indian market feeds.
- [BSE India](https://www.bseindia.com/) provides official Indian market feeds.

Market data providers should be accessed through a dedicated ingestion layer, with credentials kept in environment variables and raw and processed data separated under `data/raw` and `data/processed`.

## Models

### Sentiment

- [FinBERT](https://huggingface.co/yiyanghkust/finbert-tone) is the current sentiment model reference used by `ml/sentiment/finbert_pipeline.py`.
- [Hugging Face Transformers Course](https://huggingface.co/course/chapter1) provides background for tokenizer and transformer model usage.

### Forecasting

- The project uses hosted inference for forecasting. [Amazon Chronos-T5 Tiny](https://huggingface.co/amazon/chronos-t5-tiny) is the selected model artifact. Its model card documents a numeric context and `prediction_length`; it is not currently deployed by an Inference Provider, so use a dedicated Hugging Face Endpoint with a compatible handler.
- [TensorFlow LSTM for Stock Forecasting](https://www.tensorflow.org/tutorials/structured_data/time_series) covers recurrent time-series forecasting concepts.
- ARIMA is a potential statistical forecasting alternative. It is not currently listed as an installed dependency or implemented model.
- [Informer](https://huggingface.co/thuml/informer) is a potential transformer-based time-series alternative.
- [Prophet](https://facebook.github.io/prophet/) is another forecasting alternative and is not currently part of the installed dependency set.

### Fundamentals

- Fundamentals inference requires a task-specific hosted model or dedicated endpoint trained for the project feature schema. Hugging Face does not provide a universal serverless tabular-regression contract for arbitrary `X` and `y` payloads.
- The endpoint contract is `inputs` containing the feature matrix, with numeric predictions returned by the configured handler.

### Portfolio Optimization

- [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory), also known as Markowitz mean-variance optimization, provides the conceptual basis for portfolio allocation.
- The current optimizer in `ml/portfolio/portfolio_optimizer.py` returns an equally weighted allocation as a simplified implementation.
- Expected return, risk constraints, transaction costs, and risk limits should be added when the optimizer is expanded beyond the current baseline.

## Platform and Visualization References

- [FastAPI Documentation](https://fastapi.tiangolo.com/) covers the backend API framework and request validation.
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html) provides the deep-learning and time-series foundation used by the project. See also the [PyTorch tutorials](https://pytorch.org/tutorials/) for time-series guidance.
- [React Documentation](https://react.dev/) covers the web client.
- [Material UI Documentation](https://mui.com/material-ui/) covers the web interface components.
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/) covers chart rendering in the dashboard.

## Resource Selection Guidelines

When adding a resource or provider:

1. Record its purpose and whether it is active, planned, or an alternative.
2. Keep API keys and other credentials out of source control.
3. Validate licensing, rate limits, data quality, and geographic coverage.
4. Add an adapter or service boundary instead of coupling provider-specific code to UI components.
5. Document the resulting input and output contract in `docs/skills.md` and `docs/architecture.md`.
