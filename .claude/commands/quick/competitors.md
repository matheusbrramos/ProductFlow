# /competitors - Análise de Concorrentes

Inicia análise competitiva com @researcher (execução em paralelo).

## Uso

```
/competitors [lista de concorrentes ou segmento]
```

## Exemplos

```
/competitors Eventbrite, Ingresse, Tickets For Fun
/competitors "plataformas de ticketing no Brasil"
/competitors www.eventbrite.com.br www.ingresse.com
```

## O que acontece

1. @researcher identifica concorrentes (se não fornecidos)
2. Lança sub-agentes em paralelo (1 por concorrente)
3. Cada sub-agente pesquisa: site, reviews, notícias, LinkedIn
4. Consolida em análise unificada
5. Cria `.context/competidores-{projeto}.md`

## Outros comandos do @researcher

### Market sizing
```
/sizing "segmento de mercado"
```

### Tendências
```
/trends "segmento"
```

### Análise profunda de um player
```
/player "nome do concorrente"
```

## Pré-requisitos

- `.context/empresa.md` deve existir

## Próximos passos sugeridos

- `/prd` - Criar especificação com base nos gaps
- `/battlecard` - Criar material competitivo
