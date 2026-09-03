import pytest

from backend.services.huggingface import (
    HuggingFaceInference,
    HuggingFaceInferenceError,
    HuggingFaceSentiment,
)


class FakeResponse:
    status_code = 200
    ok = True

    def json(self):
        return [[
            {"label": "positive", "score": 0.8},
            {"label": "negative", "score": 0.1},
            {"label": "neutral", "score": 0.1},
        ]]


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse()


def test_huggingface_sentiment_normalizes_labels():
    session = FakeSession()
    inference = HuggingFaceInference(
        token="test-token", model="test-model", session=session
    )

    result = HuggingFaceSentiment(inference).analyze("Strong earnings")

    assert result == {"Positive": 0.8, "Negative": 0.1, "Neutral": 0.1}
    assert session.calls[0][1]["json"] == {"inputs": "Strong earnings"}
    assert session.calls[0][1]["headers"] == {
        "Authorization": "Bearer test-token"
    }


def test_huggingface_requires_server_side_token():
    with pytest.raises(HuggingFaceInferenceError, match="HF_API_TOKEN"):
        HuggingFaceInference(token=None, session=FakeSession()).classify("Test")