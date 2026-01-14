# /discovery - Análise de Usuários

Inicia ou continua o processo de discovery com /discovery.

## Uso

```
/discovery <ação> [dados]
```

## Ações disponíveis

### Analisar entrevistas
```
/discovery analyze [transcrições ou dados]
```

### Preparar guia de entrevista
```
/discovery interview "perfil do entrevistado"
```

### Criar/atualizar OST
```
/discovery ost "outcome de negócio"
```

### Mapear Jobs-to-be-Done
```
/discovery jtbd "segmento/contexto"
```

### Sintetizar insights
```
/discovery synthesize
```

## Exemplos

```
/discovery analyze [cole as transcrições]
/discovery interview "organizadores que fizeram só 1 evento"
/discovery ost "aumentar retenção de 30% para 45%"
/discovery jtbd "organizadores de eventos corporativos"
```

## Pré-requisitos

- `.context/empresa.md` deve existir (rode `/setup` primeiro)

## Próximos passos sugeridos

- `/competitors` - Pesquisa de mercado
- `/prd` - Criar especificação
