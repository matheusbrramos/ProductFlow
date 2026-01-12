#!/bin/bash

# ProductFlow - Script de Instalação (Linux/Mac)
# Execute na pasta raiz do seu projeto

echo "========================================"
echo "  ProductFlow - Instalação"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Verificar se já existe .claude
if [ -d ".claude" ]; then
    echo -e "${YELLOW}AVISO: Pasta .claude já existe!${NC}"
    read -p "Deseja sobrescrever? (s/n) " resposta
    if [ "$resposta" != "s" ]; then
        echo -e "${RED}Instalação cancelada.${NC}"
        exit 1
    fi
    rm -rf .claude
fi

# URL do repositório (substitua pelo seu)
REPO_URL="https://github.com/matheusbrramos/ProductFlow/archive/refs/heads/main.zip"
TEMP_ZIP="productflow-temp.zip"
TEMP_DIR="ProductFlow-main"

echo -e "${GREEN}Baixando ProductFlow...${NC}"

# Baixar ZIP
if command -v curl &> /dev/null; then
    curl -L -o "$TEMP_ZIP" "$REPO_URL"
elif command -v wget &> /dev/null; then
    wget -O "$TEMP_ZIP" "$REPO_URL"
else
    echo -e "${RED}Erro: curl ou wget não encontrado${NC}"
    exit 1
fi

# Verificar se download foi bem sucedido
if [ ! -f "$TEMP_ZIP" ]; then
    echo -e "${RED}Erro ao baixar o arquivo${NC}"
    exit 1
fi

# Extrair
echo -e "${GREEN}Extraindo arquivos...${NC}"
unzip -q "$TEMP_ZIP"

# Copiar arquivos
echo -e "${GREEN}Copiando arquivos...${NC}"
cp -r "$TEMP_DIR/.claude" .claude
cp "$TEMP_DIR/CLAUDE.md" CLAUDE.md

# Criar estrutura de pastas
echo -e "${GREEN}Criando estrutura de pastas...${NC}"

mkdir -p .context
mkdir -p docs/discovery
mkdir -p docs/research
mkdir -p docs/planning/stories
mkdir -p docs/sales/battlecards
mkdir -p docs/sales/playbooks
mkdir -p docs/sales/templates
mkdir -p docs/reviews
mkdir -p .productflow/snapshots
mkdir -p .productflow/memory

# Limpar temporários
rm -f "$TEMP_ZIP"
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ProductFlow instalado com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Estrutura criada:${NC}"
echo "  .claude/commands/agents/    - 6 agentes especializados"
echo "  .claude/commands/quick/     - Comandos rápidos"
echo "  .context/                   - Contexto do projeto"
echo "  docs/                       - Documentação gerada"
echo "  CLAUDE.md                   - Regras globais"
echo ""
echo -e "${YELLOW}Para começar, abra o Claude Code e execute:${NC}"
echo "  @helper /setup www.suaempresa.com.br"
echo ""
