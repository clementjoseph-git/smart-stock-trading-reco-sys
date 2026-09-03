# Hosted Hugging Face Endpoints

The backend uses hosted Hugging Face inference. Model credentials and endpoint URLs belong in the server environment, never in the React application.

## Verified Model

`ProsusAI/finbert` is a supported text-classification model. The backend sends:

```json
{"inputs": "Earnings exceeded expectations"}
```

The expected response is an array of `{ "label": string, "score": number }` objects. The gateway normalizes those labels to `Positive`, `Negative`, and `Neutral`.

## Forecast Endpoint

`amazon/chronos-t5-tiny` is the selected model artifact for forecasting. Its model card documents a numeric context and `prediction_length`, but it is not currently deployed by a serverless Inference Provider. Create a dedicated Hugging Face Inference Endpoint using this model and a handler that accepts:

```json
{
  "inputs": [100.0, 101.0, 102.0],
  "parameters": {"prediction_length": 5}
}
```

The handler must return a JSON object such as:

```json
{"forecast": [103.0, 104.0, 105.0, 106.0, 107.0]}
```

Configure its URL with `HF_FORECAST_ENDPOINT` and its model ID with `HF_FORECAST_MODEL`.

## Fundamentals Endpoint

There is no verified universal serverless tabular-regression model for this project schema. Select or train a Hugging Face model using the project’s defined fundamental features, then deploy it as a dedicated Endpoint. The handler receives:

```json
{
  "inputs": [[1.0, 2.0, 3.0]],
  "parameters": {"task": "fundamentals"}
}
```

It must return either `{ "predictions": [0.42] }` or `{ "predictions": [{ "value": 0.42 }] }`. Configure `HF_FUNDAMENTALS_ENDPOINT` and `HF_FUNDAMENTALS_MODEL` after the model and feature schema are finalized.

## Server Configuration

Copy `backend/.env.example` into the server environment and replace placeholders:

```text
HF_API_TOKEN=hf_...
HF_SENTIMENT_MODEL=ProsusAI/finbert
HF_FORECAST_MODEL=amazon/chronos-t5-tiny
HF_FORECAST_ENDPOINT=https://<forecast-endpoint>.endpoints.huggingface.cloud
HF_FORECAST_HORIZON=5
HF_FUNDAMENTALS_MODEL=<org>/<model>
HF_FUNDAMENTALS_ENDPOINT=https://<fundamentals-endpoint>.endpoints.huggingface.cloud
```

## Live Verification

After both dedicated endpoints are deployed, start the backend and run:

```text
POST /sentiment
POST /forecast
POST /fundamentals
POST /recommendation/live
```

Use the automated mocked tests first, then run a controlled live request with a token that has Hugging Face Inference permission. Do not place the token in source control or browser environment variables.