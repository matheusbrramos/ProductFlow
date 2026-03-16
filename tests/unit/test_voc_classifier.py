from __future__ import annotations

import os

import pytest

from play_insights.voc_classifier import classify_voc, detect_event_urgency, detect_language


def test_detect_language_prefers_portuguese() -> None:
    assert detect_language("o app esta lento e com erro no login") == "pt-BR"


def test_classify_estabilidade() -> None:
    result = classify_voc("O app trava e fecha sozinho toda vez.")
    assert result.complaint_category == "estabilidade"
    assert result.confidence >= 0.6


def test_classify_pagamento() -> None:
    result = classify_voc("Payment failed and my subscription is still charged.")
    assert result.complaint_category == "pagamento_assinatura"


# --- experiencia_compra tests ---

def test_experiencia_compra_pt() -> None:
    result = classify_voc("não consigo finalizar a compra do ingresso, o checkout trava")
    assert result.complaint_category == "experiencia_compra"


def test_experiencia_compra_qrcode() -> None:
    result = classify_voc("O qr code do ingresso não aparece no app")
    assert result.complaint_category == "experiencia_compra"


def test_experiencia_compra_en() -> None:
    result = classify_voc("checkout keeps failing every time I try to buy tickets")
    assert result.complaint_category == "experiencia_compra"


def test_experiencia_compra_confidence() -> None:
    result = classify_voc("não consigo finalizar a compra do ingresso")
    assert result.confidence >= 0.75


# --- detect_event_urgency tests ---

def test_event_urgency_detected_pt() -> None:
    assert detect_event_urgency("show hoje à noite e não consigo entrar") is True


def test_event_urgency_detected_urgente() -> None:
    assert detect_event_urgency("preciso de ajuda urgente com meu ingresso") is True


def test_event_urgency_detected_en() -> None:
    assert detect_event_urgency("the show is tonight and I can't get in") is True


def test_event_urgency_not_detected() -> None:
    assert detect_event_urgency("app muito lento quando abro o menu") is False


def test_event_urgency_not_detected_regular_complaint() -> None:
    assert detect_event_urgency("o app continua travando na tela de pagamento") is False


@pytest.mark.live_api
def test_classify_real_reviews() -> None:
    db_path = os.environ.get("DB_PATH", "play_insights.duckdb")
    from play_insights.duckdb_repo import DuckDBRepository
    from play_insights.voc_classifier import VocResult
    repo = DuckDBRepository(db_path=db_path)
    reviews = repo.query("SELECT comment_text FROM reviews_raw WHERE comment_text IS NOT NULL LIMIT 20")
    for r in reviews:
        text = r.get("comment_text") or ""
        result = classify_voc(text)
        assert isinstance(result, VocResult)
        assert result.complaint_category is not None
        assert 0 < result.confidence <= 1.0
