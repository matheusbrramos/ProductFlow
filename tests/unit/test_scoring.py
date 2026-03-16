from play_insights.scoring import infer_intent, sentiment_label, severity_score


def test_sentiment_negative_by_rating() -> None:
    assert sentiment_label("ok", 1) == "neg"


def test_sentiment_positive_by_words() -> None:
    assert sentiment_label("great app and awesome support", None) == "pos"


def test_severity_bounds() -> None:
    score = severity_score("nao funciona e crash", 1, "estabilidade")
    assert 1 <= score <= 5
    assert score >= 4


def test_intent_bug_report() -> None:
    assert infer_intent("app crash all the time", "estabilidade", 1) == "bug_report"

