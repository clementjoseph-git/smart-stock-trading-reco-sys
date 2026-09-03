import os

import requests


class HuggingFaceInferenceError(Exception):
    """Raised when a hosted Hugging Face inference request fails."""


class HuggingFaceInference:
    def __init__(self, token=None, model=None, endpoint=None, session=None, timeout=30):
        self.token = token or os.getenv("HF_API_TOKEN")
        self.model = model or os.getenv("HF_SENTIMENT_MODEL", "ProsusAI/finbert")
        self.session = session or requests
        self.timeout = timeout
        self.endpoint = endpoint or os.getenv(
            "HF_INFERENCE_URL", "https://router.huggingface.co/hf-inference/models"
        )
        self.dedicated_endpoint = endpoint is not None

    def classify(self, text):
        result = self.predict({"inputs": text})
        if isinstance(result, list) and result and isinstance(result[0], list):
            result = result[0]
        if not isinstance(result, list):
            raise HuggingFaceInferenceError(
                "Hugging Face returned an unexpected classification response"
            )
        return result

    def predict(self, payload, model=None):
        if not self.token:
            raise HuggingFaceInferenceError("HF_API_TOKEN is not configured")
        selected_model = model or self.model
        if not selected_model:
            raise HuggingFaceInferenceError("A Hugging Face model is not configured")

        try:
            url = self.endpoint if self.dedicated_endpoint else f"{self.endpoint}/{selected_model}"
            response = self.session.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            raise HuggingFaceInferenceError(
                "Hugging Face inference request failed"
            ) from error

        if response.status_code == 429:
            raise HuggingFaceInferenceError("Hugging Face rate limit exceeded")
        if not response.ok:
            raise HuggingFaceInferenceError(
                f"Hugging Face returned HTTP {response.status_code}"
            )

        try:
            result = response.json()
        except ValueError as error:
            raise HuggingFaceInferenceError(
                "Hugging Face returned invalid JSON"
            ) from error

        return result


class HuggingFaceSentiment:
    def __init__(self, inference=None):
        self.inference = inference or HuggingFaceInference()

    def analyze(self, text):
        classifications = self.inference.classify(text)
        scores = {item["label"].capitalize(): float(item["score"]) for item in classifications}
        return {
            "Positive": scores.get("Positive", 0.0),
            "Negative": scores.get("Negative", 0.0),
            "Neutral": scores.get("Neutral", 0.0),
        }


class HuggingFaceNumericModel:
    def __init__(self, task, inference=None, model=None):
        self.task = task
        self.model = model or os.getenv(f"HF_{task.upper()}_MODEL")
        endpoint = os.getenv(f"HF_{task.upper()}_ENDPOINT")
        self.inference = inference or HuggingFaceInference(
            model=self.model, endpoint=endpoint
        )

    def predict(self, values):
        if not self.model:
            raise HuggingFaceInferenceError(
                f"HF_{self.task.upper()}_MODEL is not configured"
            )
        result = self.inference.predict(
            {"inputs": values, "parameters": {"task": self.task}}, self.model
        )
        if isinstance(result, dict):
            result = result.get("forecast", result.get("predictions", result.get("outputs")))
        if isinstance(result, list) and result and isinstance(result[0], dict):
            result = [item.get("value", item.get("score")) for item in result]
        if not isinstance(result, list) or not result:
            raise HuggingFaceInferenceError(
                f"Hugging Face returned an unexpected {self.task} response"
            )
        try:
            return [float(value) for value in result]
        except (TypeError, ValueError) as error:
            raise HuggingFaceInferenceError(
                f"Hugging Face returned non-numeric {self.task} values"
            ) from error


class HuggingFaceForecast(HuggingFaceNumericModel):
    def __init__(self, inference=None, model=None, horizon=None):
        super().__init__("forecast", inference=inference, model=model)
        self.horizon = horizon or int(os.getenv("HF_FORECAST_HORIZON", "5"))

    def predict(self, values):
        if not self.model:
            raise HuggingFaceInferenceError("HF_FORECAST_MODEL is not configured")
        result = self.inference.predict(
            {"inputs": values, "parameters": {"prediction_length": self.horizon}},
            self.model,
        )
        if isinstance(result, dict):
            result = result.get("forecast", result.get("predictions", result.get("outputs")))
        if isinstance(result, list) and result and isinstance(result[0], dict):
            result = [item.get("value", item.get("score")) for item in result]
        if not isinstance(result, list) or not result:
            raise HuggingFaceInferenceError("Hugging Face returned an unexpected forecast response")
        try:
            return [float(value) for value in result]
        except (TypeError, ValueError) as error:
            raise HuggingFaceInferenceError(
                "Hugging Face returned non-numeric forecast values"
            ) from error


class HuggingFaceFundamentals(HuggingFaceNumericModel):
    def __init__(self, inference=None, model=None):
        super().__init__("fundamentals", inference=inference, model=model)
