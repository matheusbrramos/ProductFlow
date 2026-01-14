# /sales - Materiais de Vendas

Aciona /sales-enabler para criar materiais comerciais.

## Uso

```
/sales
```

Sem argumentos, apresenta catálogo completo e pergunta o que gerar.

## Comandos específicos

### Gerar material específico
```
/sales gerar <artefato> para <persona/contexto>
```

### Exemplos
```
/sales gerar battlecard para Eventbrite
/sales gerar pitch elevator
/sales gerar playbook para etapa discovery
/sales gerar talk-track para Organizador Iniciante
/sales gerar onboarding para SDR
```

### Atualizar material
```
/sales atualizar battlecard-eventbrite v1.0 → v1.1
```

### Criar treinamento
```
/sales treinamento "objeções" formato live
```

### Ver catálogo
```
/sales catalogo
```

## Materiais disponíveis

- Sales Deck
- One-pager
- Battlecards
- Playbooks por etapa
- Talk tracks
- Scripts de discovery
- Objection handling
- Guia de demo
- Email/WhatsApp templates
- Case briefs
- ROI calculator
- Onboarding 30-60-90
- FAQs e glossário
- Checklists de qualificação

## Pré-requisitos

- PRD ou specs definidos pelo @strategist
- Análise competitiva do @researcher
- Idealmente: insights do @discovery

## Próximos passos sugeridos

- `/review` - Revisar qualidade dos materiais
