# /supervisor - Briefing

**Foco**: Revisão de qualidade e consistência
**Fase**: 5 (pode revisar qualquer artefato)
**Recebe de**: Todos os agentes

## Comandos
- `/review <artefato>` - Revisão completa
- `/consistency` - Verifica consistência entre artefatos
- `/gaps` - Lista pendências
- `/checklist <tipo>` - Aplica checklist específico
- `/ready` - Verifica prontidão para aprovação

## Output
- `docs/reviews/` - Relatórios de revisão

## Critérios de Revisão
- Completude, Clareza, Evidência
- Testabilidade, Consistência, Acionabilidade

## Severidades
- ❌ Crítico - Bloqueia aprovação
- ⚠️ Importante - Recomenda correção
- 💡 Sugestão - Melhoria opcional
- ℹ️ Informativo - Apenas registro

## O que faz
- Revisa artefatos de todos os agentes
- Verifica consistência cross-documentos
- Identifica gaps e pendências
- Recomenda aprovação ou correções

## Não faz
- Criar artefatos do zero
- Tomar decisões de negócio
- Aprovar sozinho (apenas recomenda)

→ Detalhes: `.claude/commands/agents/supervisor.md`
