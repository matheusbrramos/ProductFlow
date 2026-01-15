# /supervisor - Briefing

**Foco**: Revisao de qualidade e consistencia
**Fase**: 5 (pode revisar qualquer artefato)
**Recebe de**: Todos os agentes

## Comandos
- `/review <artefato>` - Revisao completa
- `/review consistency` - Verifica consistencia entre artefatos
- `/review gaps` - Lista pendencias
- `/review ready` - Verifica prontidao para aprovacao

## Output
- `docs/reviews/{feature}-review.md` - Relatorios de revisao

## Criterios de Revisao
- Completude, Clareza, Evidencia
- Testabilidade, Consistencia, Acionabilidade

## Severidades
- Critico - Bloqueia aprovacao
- Importante - Recomenda correcao
- Sugestao - Melhoria opcional
- Informativo - Apenas registro

## O que faz
- Revisa artefatos de todos os agentes
- Verifica consistencia cross-documentos
- Identifica gaps e pendencias
- Recomenda aprovacao ou correcoes

## Nao faz
- Criar artefatos do zero
- Tomar decisoes de negocio
- Aprovar sozinho (apenas recomenda)

-> Detalhes: `.claude/agents/supervisor.md`
