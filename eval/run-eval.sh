#!/bin/bash
# =============================================================================
# ProductFlow Evaluation Runner
# Executa avaliacao de um brief e compara com estrutura esperada
# =============================================================================

set -e

EVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$EVAL_DIR")"

echo "============================================="
echo "  ProductFlow Evaluation Runner"
echo "============================================="
echo ""

# Verifica argumentos
if [ -z "$1" ]; then
    echo "Uso: ./eval/run-eval.sh <brief-id>"
    echo ""
    echo "Briefs disponiveis:"
    ls -1 "$EVAL_DIR/briefs/" | sed 's/\.md$//' | sed 's/brief-/  /'
    echo ""
    echo "Exemplo: ./eval/run-eval.sh 01-saas-simples"
    exit 1
fi

BRIEF_ID="$1"
BRIEF_FILE="$EVAL_DIR/briefs/brief-$BRIEF_ID.md"
EXPECTED_FILE="$EVAL_DIR/expected/expected-$BRIEF_ID.md"

# Verifica se brief existe
if [ ! -f "$BRIEF_FILE" ]; then
    echo "ERRO: Brief nao encontrado: $BRIEF_FILE"
    exit 1
fi

# Verifica se expected existe
if [ ! -f "$EXPECTED_FILE" ]; then
    echo "ERRO: Expected nao encontrado: $EXPECTED_FILE"
    exit 1
fi

echo "Brief: $BRIEF_FILE"
echo "Expected: $EXPECTED_FILE"
echo ""

# Limpa artefatos anteriores (opcional)
read -p "Limpar artefatos anteriores em docs/? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "Limpando..."
    rm -rf "$PROJECT_ROOT/docs/discovery/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/research/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/prd/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/sdd/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/stories/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/sales/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/docs/reviews/"* 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/.context/empresa.md" 2>/dev/null || true
    echo "Artefatos limpos."
fi

echo ""
echo "============================================="
echo "  INSTRUCOES"
echo "============================================="
echo ""
echo "1. Abra o brief para referencia:"
echo "   cat $BRIEF_FILE"
echo ""
echo "2. Execute o ProductFlow seguindo o fluxo do brief"
echo ""
echo "3. Apos conclusao, rode a verificacao:"
echo "   ./eval/check-eval.sh $BRIEF_ID"
echo ""
echo "============================================="
echo ""

# Mostra o brief
echo "--- BRIEF ---"
cat "$BRIEF_FILE"
echo ""
echo "--- FIM DO BRIEF ---"
