#!/bin/bash

# ProductFlow - Script de Instalacao (Linux/Mac)
# Execute na pasta raiz do seu projeto

echo "========================================"
echo "  ProductFlow v3.0 - Instalacao"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Verificar se ja existe .claude
if [ -d ".claude" ]; then
    echo -e "${YELLOW}AVISO: Pasta .claude ja existe!${NC}"
    read -p "Deseja sobrescrever? (s/n) " resposta
    if [ "$resposta" != "s" ]; then
        echo -e "${RED}Instalacao cancelada.${NC}"
        exit 1
    fi
    rm -rf .claude
fi

# URL do repositorio
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
    echo -e "${RED}Erro: curl ou wget nao encontrado${NC}"
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

# Copiar CLAUDE.md apenas se nao existir
if [ ! -f "CLAUDE.md" ]; then
    cp "$TEMP_DIR/CLAUDE.md" CLAUDE.md
else
    echo -e "${YELLOW}CLAUDE.md ja existe, mantendo versao atual${NC}"
fi

# Criar estrutura de pastas
echo -e "${GREEN}Criando estrutura de pastas...${NC}"

mkdir -p .context
mkdir -p docs/briefings
mkdir -p docs/templates
mkdir -p docs/discovery
mkdir -p docs/research
mkdir -p docs/prd
mkdir -p docs/stories
mkdir -p docs/sales
mkdir -p docs/reviews
mkdir -p .productflow/snapshots
mkdir -p .productflow/memory

# Copiar briefings e templates se existirem
if [ -d "$TEMP_DIR/docs/briefings" ]; then
    cp -r "$TEMP_DIR/docs/briefings/"* docs/briefings/ 2>/dev/null || true
fi
if [ -d "$TEMP_DIR/docs/templates" ]; then
    cp -r "$TEMP_DIR/docs/templates/"* docs/templates/ 2>/dev/null || true
fi

# Limpar temporarios
rm -f "$TEMP_ZIP"
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ProductFlow instalado com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Estrutura criada:${NC}"
echo "  .claude/agents/     - 7 subagents especializados"
echo "  .claude/commands/   - 8 slash commands"
echo "  .context/           - Contexto do projeto"
echo "  docs/               - Artefatos de trabalho"
echo "  .productflow/       - Estado interno"
echo "  CLAUDE.md           - Regras globais"
echo ""
echo -e "${CYAN}Slash Commands disponiveis:${NC}"
echo "  /setup     - Iniciar contexto"
echo "  /research  - Pesquisa de mercado"
echo "  /discovery - Analise de usuarios"
echo "  /prd       - Criar PRD"
echo "  /stories   - User stories"
echo "  /sales     - Materiais de vendas"
echo "  /review    - Revisao de qualidade"
echo "  /status    - Status do projeto"
echo ""
echo -e "${YELLOW}Para comecar, abra o Claude Code e execute:${NC}"
echo "  /setup www.suaempresa.com.br"
echo ""
