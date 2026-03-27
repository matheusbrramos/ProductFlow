# Brief de Avaliacao 02: Fintech Complexa

## Contexto

**Empresa**: FinFlow Pagamentos
**Site**: www.finflow.com.br
**Segmento**: Fintech - Pagamentos
**Tamanho**: 80 funcionarios
**Regulacao**: Sujeito a BACEN e LGPD

## Missao

Plataforma de pagamentos recorrentes para empresas de servicos por assinatura.

## Projeto

**Nome**: Sistema de Antecipacao de Recebiveis

**Problema**: Clientes PME precisam de capital de giro mas nao conseguem credito tradicional. Eles tem recebiveis futuros que poderiam ser antecipados.

**Objetivo**: Permitir que clientes solicitem antecipacao de recebiveis de forma automatizada, com analise de risco em tempo real.

**Concorrentes**:
- Creditas (antecipacao)
- Asaas (pagamentos + antecipacao)
- PagSeguro (capital de giro)
- Stone (credito para PME)

**Restricoes**:
- Compliance BACEN obrigatorio
- Taxa de inadimplencia maxima: 3%
- SLA de aprovacao: < 2 minutos
- Auditoria completa de todas as transacoes
- Integracao com bureau de credito (Serasa/SPC)

**Personas**:
1. Gestor Financeiro PME - Precisa de capital rapido
2. Analista de Risco FinFlow - Aprova/reprova solicitacoes
3. Compliance Officer - Garante conformidade

**Criterios de Sucesso**:
- Volume de antecipacao: R$ 10M/mes em 6 meses
- Taxa de aprovacao automatica: > 60%
- Taxa de inadimplencia: < 2%
- Tempo medio de aprovacao: < 90 segundos

## Fluxo Esperado

```
/setup www.finflow.com.br
/research Creditas, Asaas, PagSeguro, Stone
/discovery interview "Gestor Financeiro PME"
/discovery interview "Analista de Risco"
/prd "Sistema de Antecipacao de Recebiveis"
/pf-spec "Sistema de Antecipacao de Recebiveis"
/stories "Sistema de Antecipacao de Recebiveis"
/sales gerar battlecard para Creditas
/pf-review ready
```

## Complexidade

Alta

## Desafios Especificos

1. Requisitos regulatorios (BACEN, LGPD)
2. Multiplas personas com necessidades distintas
3. Requisitos nao-funcionais criticos (performance, seguranca)
4. Integracao com sistemas externos (bureaus, banking)
5. Metricas de sucesso com thresholds especificos

## Tempo Estimado de Avaliacao

60-90 minutos
