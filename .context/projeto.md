# Contexto do Projeto - Play Rating Recovery Agent

**Atualizado em:** 2026-03-03
**Owner:** Matheus Ramos
**Projeto:** App Google Reports / Play Insights

## 1. Problema / Oportunidade

- A nota do app Android esta abaixo de 1.7 e em queda.
- Falta visao consolidada entre:
  - voz do cliente (reviews),
  - qualidade tecnica (crash/ANR/erros),
  - recomendacoes priorizadas para melhorar nota e experiencia.

## 2. Objetivo do Projeto

- Construir um assistente/agente para analisar dados reais da Google Play e apoiar gestao continua de qualidade do app.
- Entregar diagnostico acionavel com:
  - classificacao de reclamacoes,
  - causas-raiz,
  - recomendacoes por impacto,
  - relatorio diario e semanal.

## 3. Escopo (MVP)

### Incluido
- Coleta de dados reais de:
  - Google Play Reviews API
  - Google Play Developer Reporting API (vitals/erros)
- Classificacao VOC (PT-BR + EN)
- Priorizacao de acoes
- Relatorios:
  - diario (`docs/discovery/play-voc-YYYY-MM-DD.md`)
  - semanal (`docs/research/play-quality-YYYY-MM-DD.md`)
- Dry-run de respostas para reviews

### Fora do escopo imediato
- Publicacao automatica de respostas sem governanca
- Jornada in-app detalhada via GA4/Firebase (V2)

## 4. Metricas de Sucesso

- Tendencia de nota media para estabilizacao e recuperacao.
- Reducao de volume de reviews 1-2 estrelas por semana.
- Identificacao semanal de top causas e plano de acao correspondente.
- [ASSUMPTION] Primeiros ganhos observaveis em 2-6 semanas apos operacao continua.

## 5. Premissas

- [ASSUMPTION] Existe acesso valido ao Play Console para o app `br.com.quero2ingressos`.
- [ASSUMPTION] As APIs Google necessarias estao habilitadas no projeto GCP `217558870344`.
- [ASSUMPTION] Credencial de service account sera armazenada fora de versionamento.
- [ASSUMPTION] O time quer manter o fluxo ProductFlow como camada de operacao/documentacao.

## 6. Restricoes

- Nao usar dados mock para validacoes de API e pipeline.
- Evitar exposicao de dados sensiveis em artifacts.
- Resposta automatica a reviews deve permanecer desligada por padrao.

## 7. Stakeholders

- Product: Matheus Ramos
- Engenharia Mobile: [NEEDS CLARIFICATION]
- Suporte/Atendimento: [NEEDS CLARIFICATION]
- Gestao executiva: [NEEDS CLARIFICATION]

## 8. Stack e Arquitetura de Dados

- Implementacao atual no repositorio:
  - Python + pytest
  - cliente Play APIs
  - pipeline CLI `python -m play_insights ...`
- Persistencia:
  - [NEEDS CLARIFICATION] Migrar de BigQuery para DuckDB agora, ou manter BigQuery no MVP e migrar em fase seguinte?
  - [ASSUMPTION] Existe trilha paralela para DuckDB em andamento.

## 9. Dependencias Externas

- Google Play Console (API access)
- Google Cloud IAM + Service Account
- APIs Google (Publisher / Reporting / BigQuery se mantido)

## 10. Riscos Principais

- Permissao incompleta no Play Console causar erro 403.
- Quotas/API instability impactarem ingestao.
- Mudanca de storage (BigQuery -> DuckDB) gerar desalinhamento temporario no pipeline.

## 11. Proximos Passos Recomendados

1. Fechar Bloco A em `todo_Matheus.md` com evidencias.
2. Validar auth live (`pytest -m live_api -k auth`).
3. Rodar ingestao e analise ponta a ponta.
4. Definir decisao final de storage (BigQuery vs DuckDB) e ajustar codigo conforme decisao.

