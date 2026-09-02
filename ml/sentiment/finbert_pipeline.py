from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinBERTSentiment:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

    def analyze(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = ["Positive", "Negative", "Neutral"]
        return dict(zip(labels, probs[0].detach().numpy().tolist()))
