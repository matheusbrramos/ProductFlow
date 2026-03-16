from __future__ import annotations


NEGATIVE_WORDS = {
    "ruim",
    "pessimo",
    "horrivel",
    "travando",
    "erro",
    "fail",
    "bad",
    "terrible",
    "slow",
}
POSITIVE_WORDS = {"otimo", "excelente", "bom", "good", "great", "awesome", "recomendo"}


def sentiment_label(text: str, star_rating: int | None) -> str:
    txt = text.lower()
    if star_rating is not None:
        if star_rating <= 2:
            return "neg"
        if star_rating >= 4:
            return "pos"
    neg_hits = sum(1 for token in NEGATIVE_WORDS if token in txt)
    pos_hits = sum(1 for token in POSITIVE_WORDS if token in txt)
    if neg_hits > pos_hits:
        return "neg"
    if pos_hits > neg_hits:
        return "pos"
    return "neu"


def severity_score(text: str, star_rating: int | None, category: str) -> int:
    from play_insights.voc_classifier import detect_event_urgency  # local import avoids circular
    score = 3
    txt = text.lower()
    if star_rating is not None and star_rating <= 2:
        score += 1
    if category in {"estabilidade", "pagamento_assinatura", "funcionalidade_quebrada", "experiencia_compra"}:
        score += 1
    if any(token in txt for token in {"nao funciona", "impossivel", "bloqueado", "crash"}):
        score += 1
    if detect_event_urgency(text):
        score += 1
    return max(1, min(5, score))


def infer_intent(text: str, category: str, star_rating: int | None) -> str:
    txt = text.lower()
    if any(token in txt for token in {"seria bom", "poderia", "feature", "gostaria"}):
        return "feature_request"
    if any(token in txt for token in {"suporte", "support", "ajuda", "help"}):
        return "support_request"
    if category in {"estabilidade", "funcionalidade_quebrada"}:
        return "bug_report"
    if star_rating is not None and star_rating <= 2:
        return "frustration"
    return "praise"

