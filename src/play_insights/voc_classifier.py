from __future__ import annotations

import re
from dataclasses import dataclass


PT_HINTS = {"nao", "app", "lento", "erro", "falha", "login", "pagamento"}
EN_HINTS = {"app", "slow", "error", "crash", "login", "payment", "support"}


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "estabilidade": ("crash", "trav", "fecha sozinho", "falha", "anr", "bug"),
    "performance": ("lento", "slow", "demora", "loading", "travando"),
    "login_autenticacao": ("login", "senha", "password", "entrar", "autentic"),
    "pagamento_assinatura": ("pagamento", "cobr", "assinatura", "refund", "payment"),
    "usabilidade": ("dificil", "confuso", "ux", "interface", "navegar"),
    "funcionalidade_quebrada": ("nao funciona", "broken", "erro ao", "fail to", "parou"),
    "conteudo_confiabilidade": ("informacao", "incorreto", "wrong", "data errada", "inconsistente"),
    "suporte_comunicacao": ("suporte", "support", "atendimento", "resposta", "help"),
    "experiencia_compra": (
        "checkout", "finalizar compra", "finalizar a compra", "qr code", "qrcode",
        "ingresso", "assento", "mapa de assentos", "selecao de lugar", "confirmacao",
        "ticket", "pix", "cartao", "boleto", "parcela", "ingressos",
        "comprar ingresso", "compra travou", "seat selection", "purchase",
        "payment failed", "buy tickets",
    ),
}

_EVENT_URGENCY_KEYWORDS_PT = (
    "hoje", "agora", "amanha", "show hoje", "evento hoje",
    "nao consegui entrar", "perdi o show", "perderei", "cancelar",
    "emergencia", "urgente",
)

_EVENT_URGENCY_KEYWORDS_EN = (
    "tonight", "right now", "lost my ticket", "can't get in",
    "urgent", "emergency", "missing show",
)


@dataclass
class VocResult:
    complaint_category: str
    confidence: float
    topic_keywords: str
    language: str


def detect_language(text: str) -> str:
    text_l = text.lower()
    pt_score = sum(1 for token in PT_HINTS if token in text_l)
    en_score = sum(1 for token in EN_HINTS if token in text_l)
    if pt_score >= en_score:
        return "pt-BR"
    return "en"


def normalize_text(text: str) -> str:
    text_l = text.lower().strip()
    text_l = re.sub(r"\s+", " ", text_l)
    return text_l


def detect_event_urgency(text: str) -> bool:
    """Return True if the review text signals urgency around an event (e.g. show tonight)."""
    normalized = text.lower()
    for kw in _EVENT_URGENCY_KEYWORDS_PT:
        if kw in normalized:
            return True
    for kw in _EVENT_URGENCY_KEYWORDS_EN:
        if kw in normalized:
            return True
    return False


def classify_voc(text: str) -> VocResult:
    normalized = normalize_text(text)
    language = detect_language(normalized)

    best_category = "usabilidade"
    best_keywords: list[str] = []
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in normalized]
        if len(matched) > best_score:
            best_score = len(matched)
            best_category = category
            best_keywords = matched

    # experiencia_compra gets a higher base confidence (domain-specific keywords)
    if best_category == "experiencia_compra":
        confidence = 0.75 if best_score >= 1 else 0.55
    else:
        confidence = 0.55 if best_score == 0 else min(0.99, 0.60 + (0.1 * best_score))
    return VocResult(
        complaint_category=best_category,
        confidence=confidence,
        topic_keywords=",".join(best_keywords),
        language=language,
    )

