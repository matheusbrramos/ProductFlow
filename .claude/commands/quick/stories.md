# /stories - Criar User Stories Detalhadas

Cria user stories detalhadas com /story-writer.

## Uso

```
/stories <prd ou feature>
```

## Exemplos

```
/stories "PRD de alertas inteligentes"
/stories "Feature de autenticação"
/stories docs/planning/prd-dashboard.md
```

## O que acontece

1. O agente pergunta qual modelo LLM usar (completo, econômico ou automático)
2. Analisa o PRD ou feature fornecido
3. Quebra em user stories detalhadas
4. Escreve acceptance criteria em Gherkin
5. Mapeia dependências entre stories

## Outros comandos do /story-writer

### Expandir uma story
```
/expand US-001
```

### Refinar acceptance criteria
```
/criteria US-001
```

### Dividir story grande
```
/split US-001
```

### Criar story map
```
/map "feature"
```

### Estimar complexidade
```
/estimate US-001, US-002, US-003
```

### Mapear dependências
```
/dependencies US-001, US-002
```

## Pré-requisitos

- PRD aprovado (criado por /strategist)
- `.context/empresa.md` deve existir

## Próximos passos sugeridos

- `/review stories` - Revisar qualidade das stories
- Entregar para time de desenvolvimento
