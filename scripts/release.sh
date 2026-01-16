#!/bin/bash
#
# ProductFlow Release Script
# Gera um zip limpo a partir do git, sem arquivos de workspace.
#
# Uso:
#   ./scripts/release.sh [versao]
#   ./scripts/release.sh 3.1
#

set -e

VERSION="${1:-$(date +%Y%m%d)}"
OUTPUT="ProductFlow-v${VERSION}.zip"

echo "============================================"
echo "  ProductFlow Release Builder"
echo "============================================"
echo ""
echo "Versao: ${VERSION}"
echo "Output: ${OUTPUT}"
echo ""

# Verifica se estamos em um repo git
if [ ! -d ".git" ]; then
    echo "ERRO: Execute este script na raiz do repositorio git"
    exit 1
fi

# Verifica se ha mudancas nao commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "AVISO: Ha mudancas nao commitadas. Considere commitar antes do release."
    read -p "Continuar mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Cria o zip usando git archive (ignora .git e arquivos nao rastreados)
echo "Criando arquivo ${OUTPUT}..."
git archive --format=zip --prefix=ProductFlow/ HEAD > "${OUTPUT}"

echo ""
echo "Release criado com sucesso!"
echo ""
echo "Arquivos incluidos (apenas rastreados pelo git):"
git archive --format=tar HEAD | tar -t | head -20
echo "..."
echo ""
echo "Para verificar o conteudo:"
echo "  unzip -l ${OUTPUT}"
