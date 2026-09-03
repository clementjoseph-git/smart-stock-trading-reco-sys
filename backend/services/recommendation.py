from dataclasses import dataclass


@dataclass(frozen=True)
class Recommendation:
    signal: str
    confidence: float
    score: float
    rationale: list[str]


def generate_recommendation(
    fundamental_score: float,
    technical_score: float,
    sentiment_score: float,
) -> Recommendation:
    score = (
        fundamental_score * 0.4
        + technical_score * 0.35
        + sentiment_score * 0.25
    )
    if score >= 0.65:
        signal = "BUY"
    elif score <= 0.35:
        signal = "SELL"
    else:
        signal = "HOLD"

    rationale = []
    for name, value in (
        ("Fundamentals", fundamental_score),
        ("Technical trend", technical_score),
        ("Market sentiment", sentiment_score),
    ):
        if value >= 0.6:
            rationale.append(f"Positive {name.lower()} score")
        elif value <= 0.4:
            rationale.append(f"Negative {name.lower()} score")

    if not rationale:
        rationale.append("Signals are mixed")

    return Recommendation(
        signal=signal,
        confidence=round(abs(score - 0.5) * 2, 4),
        score=round(score, 4),
        rationale=rationale,
    )
