#!/bin/bash

# ProductFlow - Script de Instalacao Nao-Destrutiva (Linux/Mac)
# Execute na pasta raiz do seu projeto

echo "========================================"
echo "  ProductFlow v3.1 - Instalacao"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Timestamp para backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=".productflow-backup-$TIMESTAMP"

# URL do repositorio
REPO_URL="https://github.com/matheusbrramos/ProductFlow/archive/refs/heads/main.zip"
TEMP_ZIP="productflow-temp.zip"
TEMP_DIR="ProductFlow-main"

# Funcao para fazer backup de um arquivo/pasta
backup_if_exists() {
    local path="$1"
    if [ -e "$path" ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r "$path" "$BACKUP_DIR/"
        echo -e "${YELLOW}  Backup criado: $BACKUP_DIR/$(basename $path)${NC}"
    fi
}

# Funcao para merge seguro de diretorio
safe_merge_dir() {
    local src="$1"
    local dest="$2"

    if [ ! -d "$src" ]; then
        return
    fi

    mkdir -p "$dest"

    for file in "$src"/*; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            if [ -f "$dest/$filename" ]; then
                echo -e "${YELLOW}  Arquivo existente preservado: $dest/$filename${NC}"
                # Copia versao nova com sufixo .new
                cp "$file" "$dest/$filename.new"
            else
                cp "$file" "$dest/"
            fi
        fi
    done
}

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

# Verificar se ja existe .claude (instalacao anterior ou projeto existente)
if [ -d ".claude" ]; then
    echo -e "${YELLOW}AVISO: Pasta .claude ja existe!${NC}"
    echo -e "${YELLOW}Fazendo backup e merge seguro...${NC}"

    # Backup completo
    backup_if_exists ".claude"

    # Merge seguro de agents
    echo -e "${GREEN}Atualizando agents...${NC}"
    safe_merge_dir "$TEMP_DIR/.claude/agents" ".claude/agents"

    # Merge seguro de commands
    echo -e "${GREEN}Atualizando commands...${NC}"
    safe_merge_dir "$TEMP_DIR/.claude/commands" ".claude/commands"
else
    echo -e "${GREEN}Instalando .claude/...${NC}"
    cp -r "$TEMP_DIR/.claude" .claude
fi

# CLAUDE.md - apenas se nao existir ou com confirmacao
if [ -f "CLAUDE.md" ]; then
    echo -e "${YELLOW}CLAUDE.md ja existe, mantendo versao atual${NC}"
    cp "$TEMP_DIR/CLAUDE.md" "CLAUDE.md.new"
    echo -e "${CYAN}  Nova versao salva em CLAUDE.md.new para comparacao${NC}"
else
    cp "$TEMP_DIR/CLAUDE.md" CLAUDE.md
fi

# Criar estrutura de pastas (nunca sobrescreve existentes)
echo -e "${GREEN}Criando estrutura de pastas...${NC}"

mkdir -p .context
mkdir -p docs/briefings
mkdir -p docs/templates
mkdir -p docs/discovery
mkdir -p docs/research
mkdir -p docs/prd
mkdir -p docs/sdd
mkdir -p docs/stories
mkdir -p docs/sales
mkdir -p docs/reviews
mkdir -p .productflow/snapshots
mkdir -p .productflow/memory
mkdir -p scripts

# Copiar briefings e templates (merge seguro)
if [ -d "$TEMP_DIR/docs/briefings" ]; then
    safe_merge_dir "$TEMP_DIR/docs/briefings" "docs/briefings"
fi
if [ -d "$TEMP_DIR/docs/templates" ]; then
    safe_merge_dir "$TEMP_DIR/docs/templates" "docs/templates"
fi

# Copiar validador
if [ -f "$TEMP_DIR/scripts/validate_productflow.py" ]; then
    cp "$TEMP_DIR/scripts/validate_productflow.py" "scripts/"
fi

# Limpar temporarios
rm -f "$TEMP_ZIP"
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ProductFlow instalado com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Backup criado em: $BACKUP_DIR${NC}"
    echo ""
fi

echo -e "${CYAN}Estrutura criada:${NC}"
echo "  .claude/agents/     - 7 subagents especializados"
echo "  .claude/commands/   - 10 slash commands"
echo "  .context/           - Contexto do projeto"
echo "  docs/               - Artefatos de trabalho"
echo "  docs/sdd/           - Software Design Documents"
echo "  .productflow/       - Estado interno"
echo "  scripts/            - Utilitarios"
echo "  CLAUDE.md           - Regras globais"
echo ""
echo -e "${CYAN}Slash Commands disponiveis:${NC}"
echo "  /setup       - Iniciar contexto"
echo "  /research    - Pesquisa de mercado"
echo "  /discovery   - Analise de usuarios"
echo "  /prd         - Criar PRD"
echo "  /pf-spec     - Criar SDD"
echo "  /stories     - User stories"
echo "  /sales       - Materiais de vendas"
echo "  /pf-review   - Revisao de qualidade"
echo "  /pf-status   - Status do projeto"
echo "  /pf-init     - Ajuda rapida"
echo ""
echo -e "${CYAN}Para validar a instalacao:${NC}"
echo "  python scripts/validate_productflow.py"
echo ""
echo -e "${YELLOW}Para comecar, abra o Claude Code e execute:${NC}"
echo "  /setup www.suaempresa.com.br"
echo ""
