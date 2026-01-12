# /review - Revisão de Qualidade

Aciona @supervisor para revisar artefatos.

## Uso

```
/review [artefato ou comando]
```

## Comandos disponíveis

### Revisar artefato específico
```
/review docs/planning/prd-alertas.md
/review docs/sales/battlecard-eventbrite.md
```

### Verificar consistência geral
```
/review consistency
```

### Listar gaps e pendências
```
/review gaps
```

### Aplicar checklist específico
```
/review checklist prd
/review checklist story
/review checklist battlecard
```

### Verificar se está pronto para aprovação
```
/review ready
```

## O que é verificado

- **Completude**: Todas as seções obrigatórias presentes
- **Clareza**: Sem ambiguidades
- **Evidência**: Afirmações têm suporte
- **Testabilidade**: Requisitos verificáveis
- **Consistência**: Alinhamento entre artefatos
- **Acionabilidade**: Possível agir com base no documento

## Níveis de severidade

- ❌ **Crítico**: Bloqueia aprovação
- ⚠️ **Importante**: Recomenda correção
- 💡 **Sugestão**: Melhoria opcional
- ℹ️ **Informativo**: Apenas observação

## Quando usar

- Antes de aprovar qualquer artefato
- Antes de iniciar implementação
- Antes de publicar materiais de vendas
- Ao finalizar uma fase do projeto

## Pré-requisitos

- Artefatos criados pelos outros agentes
