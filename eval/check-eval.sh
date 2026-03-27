#!/bin/bash
# =============================================================================
# ProductFlow Evaluation Checker
# Verifica se os artefatos gerados correspondem ao esperado
# =============================================================================

set -e

EVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$EVAL_DIR")"

echo "============================================="
echo "  ProductFlow Evaluation Checker"
echo "============================================="
echo ""

# Verifica argumentos
if [ -z "$1" ]; then
    echo "Uso: ./eval/check-eval.sh <brief-id>"
    exit 1
fi

BRIEF_ID="$1"
EXPECTED_FILE="$EVAL_DIR/expected/expected-$BRIEF_ID.md"

if [ ! -f "$EXPECTED_FILE" ]; then
    echo "ERRO: Expected nao encontrado: $EXPECTED_FILE"
    exit 1
fi

echo "Verificando artefatos para: $BRIEF_ID"
echo ""

# Contadores
TOTAL=0
FOUND=0
MISSING=0

check_file() {
    local path="$1"
    local desc="$2"
    TOTAL=$((TOTAL + 1))

    # Suporta wildcards
    if ls $PROJECT_ROOT/$path 1> /dev/null 2>&1; then
        echo "[OK] $desc"
        echo "     -> $(ls $PROJECT_ROOT/$path | head -1)"
        FOUND=$((FOUND + 1))
    else
        echo "[MISSING] $desc"
        echo "     -> Esperado: $path"
        MISSING=$((MISSING + 1))
    fi
}

echo "--- ARQUIVOS ---"
echo ""

# Verifica arquivos essenciais
check_file ".context/empresa.md" "Contexto da empresa"
check_file "docs/research/*.md" "Pesquisa de mercado"
check_file "docs/prd/*.md" "PRD"
check_file "docs/stories/*.md" "User Stories"
check_file "docs/reviews/*.md" "Review"

# Verifica opcionais baseado na complexidade
if grep -q "Complexidade.*Alta" "$EXPECTED_FILE" 2>/dev/null; then
    echo ""
    echo "--- ARQUIVOS OPCIONAIS (Complexidade Alta) ---"
    echo ""
    check_file "docs/sdd/*.md" "Software Design Document"
    check_file "docs/discovery/*.md" "Discovery"
    check_file "docs/sales/battlecard*.md" "Battlecard"
fi

echo ""
echo "============================================="
echo "  SUMARIO"
echo "============================================="
echo ""
echo "Total verificado: $TOTAL"
echo "Encontrados: $FOUND"
echo "Faltando: $MISSING"
echo ""

if [ $MISSING -eq 0 ]; then
    echo "STATUS: COMPLETO"
    echo ""
    echo "Proximo passo: Revisar qualidade com a rubrica"
    echo "  cat $EVAL_DIR/rubric.md"
else
    echo "STATUS: INCOMPLETO"
    echo ""
    echo "Arquivos faltando. Verifique se o fluxo foi executado corretamente."
fi

echo ""
echo "============================================="
echo "  VERIFICACAO DE QUALIDADE"
echo "============================================="
echo ""

# Verificacoes basicas de qualidade
echo "Verificando qualidade basica..."
echo ""

# PRD tem metricas?
PRD_FILE=$(ls $PROJECT_ROOT/docs/prd/*.md 2>/dev/null | head -1)
if [ -n "$PRD_FILE" ]; then
    if grep -q "Metrica" "$PRD_FILE" 2>/dev/null; then
        echo "[OK] PRD contem secao de metricas"
    else
        echo "[WARN] PRD pode estar sem metricas de sucesso"
    fi

    if grep -q "NEEDS CLARIFICATION\|NEEDS_INPUT\|PLACEHOLDER" "$PRD_FILE" 2>/dev/null; then
        echo "[INFO] PRD contem marcadores de pendencia (esperado)"
    fi
fi

# Stories tem Gherkin?
STORIES_FILE=$(ls $PROJECT_ROOT/docs/stories/*.md 2>/dev/null | head -1)
if [ -n "$STORIES_FILE" ]; then
    if grep -q "Given\|When\|Then" "$STORIES_FILE" 2>/dev/null; then
        echo "[OK] Stories contem Gherkin"
    else
        echo "[WARN] Stories podem estar sem acceptance criteria em Gherkin"
    fi
fi

echo ""
echo "Para avaliacao completa, use a rubrica em: eval/rubric.md"
