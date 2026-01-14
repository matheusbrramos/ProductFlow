# /prd - Criar Product Requirements Document

Cria PRD completo com /strategist.

## Uso

```
/prd <nome da feature ou produto>
```

## Exemplos

```
/prd "Alertas inteligentes de vendas"
/prd "Sistema de autenticação"
/prd "Módulo de relatórios"
```

## O que é gerado

PRD completo incluindo:
- Sumário executivo com problema e evidências
- Personas e Jobs-to-be-Done
- Requisitos Funcionais detalhados
- Requisitos Não-Funcionais completos
- Escopo (in/out)
- User Stories com acceptance criteria
- Métricas de sucesso
- Riscos e dependências

## Outros comandos do /strategist

### Quick Spec (features simples)
```
/spec "feature"
```

### Apenas user stories
```
/stories "prd ou feature"
```

### Priorizar features
```
/prioritize feature1, feature2, feature3
```

### Detalhar requisitos
```
/requirements "feature"
```

### Analisar problema
```
/analyze "descrição do problema"
```

## Pré-requisitos

- `.context/empresa.md` deve existir
- Recomendado: Discovery e pesquisa de mercado concluídos

## Próximos passos sugeridos

- `/review prd` - Revisar qualidade do PRD
- `/sales` - Criar materiais de vendas
