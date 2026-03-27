#!/bin/bash
# =============================================================================
# ProductFlow Release Script
# Gera um zip limpo a partir do git, sem arquivos de workspace ou sensíveis.
#
# Uso:
#   ./scripts/release.sh [versao]
#   ./scripts/release.sh 3.2
#
# Requisitos:
#   - Git instalado
#   - Executar na raiz do repositório
# =============================================================================

set -e

VERSION="${1:-$(date +%Y%m%d)}"
OUTPUT_DIR="dist"
OUTPUT="ProductFlow-v${VERSION}.zip"

echo "============================================="
echo "  ProductFlow Release Builder v3.2"
echo "============================================="
echo ""
echo "Versao: ${VERSION}"
echo "Output: ${OUTPUT_DIR}/${OUTPUT}"
echo ""

# Verifica se estamos em um repo git
if [ ! -d ".git" ]; then
    echo "ERRO: Execute este script na raiz do repositorio git"
    echo "      cd ProductFlow && ./scripts/release.sh"
    exit 1
fi

# Cria diretório de saída
mkdir -p "${OUTPUT_DIR}"

# Verifica se ha mudancas nao commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "AVISO: Ha mudancas nao commitadas. Considere commitar antes do release."
    read -p "Continuar mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Validação de segurança: verifica se settings.local.json está no .gitignore
if git ls-files --cached | grep -q "settings.local.json"; then
    echo "ERRO: settings.local.json está versionado! Remova antes do release:"
    echo "      git rm --cached .claude/settings.local.json"
    exit 1
fi

# Cria o zip usando git archive (ignora .git e arquivos nao rastreados)
echo "Criando arquivo ${OUTPUT}..."
git archive --format=zip --prefix=ProductFlow/ HEAD > "${OUTPUT_DIR}/${OUTPUT}"

# Move para diretório de saída e mostra resultado
echo ""
echo "============================================="
echo "  Release criado com sucesso!"
echo "============================================="
echo ""
echo "Caminho: ${OUTPUT_DIR}/${OUTPUT}"
echo "Tamanho: $(du -h "${OUTPUT_DIR}/${OUTPUT}" | cut -f1)"
echo ""
echo "Arquivos incluidos (apenas rastreados pelo git):"
echo "---------------------------------------------"
git archive --format=tar HEAD | tar -t | grep -E "\.(md|sh|ps1|py|json)$" | head -25
echo "..."
echo ""
echo "Validacao:"
echo "  - settings.local.json: $(git ls-files --cached | grep -q 'settings.local.json' && echo 'INCLUSO (ERRO!)' || echo 'NAO incluso (OK)')"
echo "  - .quarantine/: $(git ls-files --cached | grep -q '.quarantine' && echo 'INCLUSO (ERRO!)' || echo 'NAO incluso (OK)')"
echo ""
echo "Para verificar o conteudo completo:"
echo "  unzip -l ${OUTPUT_DIR}/${OUTPUT}"
echo ""
echo "Para instalar a partir do release:"
echo "  unzip ${OUTPUT_DIR}/${OUTPUT} && cd ProductFlow && ./install.sh"
