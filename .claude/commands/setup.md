---
description: Iniciar contexto do projeto coletando informacoes da empresa
argument-hint: <site ou nome da empresa>
---

# /setup - Iniciar Contexto do Projeto

Inicia a coleta de contexto da empresa usando o agente Helper.

## Entrada

```
$ARGUMENTS
```

Se nenhum argumento for fornecido, pergunte ao PM o site ou nome da empresa.

## O que fazer

1. **Verificar se `.context/empresa.md` ja existe**
   - Se existir, perguntar se quer atualizar ou criar novo projeto

2. **Pesquisar proativamente informacoes publicas**
   - Acessar site da empresa (se URL fornecida)
   - Buscar no LinkedIn, noticias, Crunchbase
   - Coletar: missao, produtos, publico-alvo, diferenciais

3. **Apresentar o que foi encontrado**
   - Mostrar dados coletados organizados
   - Destacar fontes consultadas

4. **Fazer apenas perguntas sobre informacoes internas**
   - Qual projeto/oportunidade vamos trabalhar?
   - Por que agora? (timing, urgencia)
   - Quem sao os stakeholders?
   - Quais as restricoes?
   - Criterios de sucesso?

5. **Criar arquivo de contexto**
   - Salvar em `.context/empresa.md`
   - Documentar todas as fontes

## Output

Criar/atualizar: `.context/empresa.md`

## Proximos passos sugeridos

Ao finalizar, sugerir:
- `/research <concorrentes>` - Mapear concorrentes
- `/discovery` - Iniciar discovery de usuarios

## Exemplos

```
/setup www.sympla.com.br
/setup "Nubank"
/setup minha-startup.com
```
