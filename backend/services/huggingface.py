import os

import requests


class HuggingFaceInferenceError(Exception):
    """Raised when a hosted Hugging Face inference request fails."""


class HuggingFaceInference:
    def __init__(self, token=None, model=None, session=None, timeout=30):
        self.token = token or os.getenv("HF_API_TOKEN")
        self.model = model or os.getenv(
            "HF_SENTIMENT_MODEL", "ProsusAI/finbert"
        )
        self.session = session or requests
        self.timeout = timeout
        self.endpoint = os.getenv(
            "HF_INFERENCE_URL", "https://router.huggingface.co/hf-inference/models"
        )

    def classify(self, text):
        if not self.token:
            raise HuggingFaceInferenceError("HF_API_TOKEN is not configured")

        try:
            response = self.session.post(
                f"{self.endpoint}/{self.model}",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"inputs": text},
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

        if isinstance(result, list) and result and isinstance(result[0], list):
            result = result[0]
        if not isinstance(result, list):
            raise HuggingFaceInferenceError(
                "Hugging Face returned an unexpected classification response"
            )
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
