# Programa Simplificado de Recuperacao e Migracao Q2 Mobile para Expo + React

**Data:** 06-03-2026  
**Autor:** Matheus Ramos  
**Owner:** Matheus Ramos  
**Sponsor Executivo:** CTO  
**Horizonte inicial:** 8 a 9 semanas  
**Direcao:** confiabilidade + paridade web/app + recuperacao reputacional como consequencia operacional

---

## 1. Contexto e Baseline

A Q2 precisa substituir o enquadramento do programa mobile. O plano anterior foi construido quando ainda havia pouca visibilidade de baseline e a discussao estava centrada em corrigir um app nativo existente. O contexto atual e diferente em tres pontos:

1. Ja existe baseline real do Google Play.
2. A direcao tecnica agora e migrar para `Expo + React`, com base compartilhada entre site e app.
3. O programa precisa ser praticavel, com poucas frentes, menos dependencias e foco em jornadas criticas.

### 1.1 Baseline validado em 05-03-2026

**Google Play, janela de 90 dias**

- Rating medio: `1.0/5`
- Reviews: `3`
- Reviews negativas: `100%`
- Crash rate medio: `24.47%`
- Dias com dados de vitals: `60`
- ANR rate medio: `0.00%`

**Principais sinais do baseline**

- O maior problema tecnico observavel hoje e estabilidade.
- Os reviews recentes nao falam de crash com a mesma intensidade do problema tecnico, o que sugere desinstalacao silenciosa ou abandono sem review.
- A principal dor visivel para o usuario continua sendo jornada critica mal resolvida: compra, acesso ao ingresso e previsibilidade.

### 1.2 Baseline provisoria da App Store

Para iOS, o repositorio nao contem export operacional equivalente ao Google Play. Portanto, o baseline numerico da App Store permanece provisoriamente ancorado nos desk researches de `10-12-2025`, ate existir coleta continua de App Store.

### 1.3 Reenquadramento do problema

O problema principal deixa de ser "como salvar um app nativo com muitos defeitos" e passa a ser:

> Como reconstruir as jornadas criticas em uma base unica Expo + React, com comportamento consistente entre web e app, de modo que a reputacao nas lojas melhore porque o produto voltou a funcionar de forma confiavel.

---

## 2. Arquitetura Alvo

### 2.1 Decisao de arquitetura

O v1 da nova fase do programa sera construido com:

- `Expo + React` como shell mobile.
- `Expo development builds` como padrao de desenvolvimento, QA em device e homologacao.
- `Expo Router` + `React Native Web` para compartilhar estrutura de rotas e comportamento entre app e site.
- Shared code obrigatorio para:
  - cliente de API
  - autenticacao e sessao
  - validacoes de formularios
  - taxonomia de erros
  - analytics e eventos
  - componentes das jornadas criticas

### 2.2 Regra de simplicidade

Tudo o que puder ser resolvido uma unica vez para web e app deve ser resolvido uma unica vez.

Somente permanecem como adaptadores de plataforma:

- review nativo/in-app
- integracoes estritamente nativas
- comportamento de abertura de loja
- eventuais recursos de device que nao tenham equivalente web

### 2.3 Escopo funcional do v1

Entram no v1:

- login e cadastro
- compra e checkout
- acesso ao ingresso
- suporte e ajuda
- telemetria e observabilidade
- fluxo de review/avaliacao

Ficam fora do v1, salvo exigencia legal ou operacional:

- biometria customizada
- wallet/passbook avancado
- qualquer funcionalidade nativa que obrigue fork de comportamento ou manutencao paralela web/app

### 2.4 Contrato de jornada compartilhado

O produto passa a operar com um contrato unico entre web e app para quatro jornadas:

| Jornada | Objetivo | Minimo obrigatorio no v1 |
|---|---|---|
| `login` | entrar ou recuperar acesso | login funcional, validacao clara, retomada de sessao |
| `checkout` | concluir compra sem bloqueio | sucesso, erro conhecido, timeout e retentativa previsiveis |
| `tickets` | acessar ingresso com seguranca | ingresso visivel, fallback de acesso, mensagens de contingencia |
| `support` | pedir ajuda sem friccao | FAQ, canal claro e abertura de contato sem loop |

---

## 3. Plano Simplificado por Fases

### Fase 1 - Rebaseline e contrato de jornada

**Duracao:** 1 semana

**Objetivo**

Transformar o programa em um plano operacional ancorado em fatos e congelar o contrato de jornada compartilhado.

**Entregas**

- consolidacao do baseline real do Google Play
- baseline provisoria da App Store referenciada e sinalizada como parcial
- definicao dos SLOs do programa
- mapa final das jornadas `login`, `checkout`, `tickets` e `support`
- definicao da taxonomia unica de erros e eventos

**Criterio de saida**

- baseline aprovado
- contrato de jornada fechado
- prioridades de v1 sem itens nativos fora do escopo

### Fase 2 - Fundacao Expo compartilhada

**Duracao:** 2 semanas

**Objetivo**

Criar a base unica onde web e app passam a compartilhar a maior parte da implementacao relevante.

**Entregas**

- app shell Expo
- estrutura de rotas em Expo Router
- design system base reaproveitavel
- modulo unico de sessao e API
- modulo unico de analytics e observabilidade
- adaptadores minimos por plataforma

**Criterio de saida**

- base rodando em web e app
- development build disponivel para testes
- logs, erros e eventos trafegando corretamente

### Fase 3 - Reconstrucao das jornadas criticas

**Duracao:** 3 a 4 semanas

**Objetivo**

Colocar as jornadas que mais afetam reputacao em producao sobre a base nova.

**Entregas**

- login/cadastro reconstruidos na base compartilhada
- checkout reconstruido na base compartilhada
- acesso ao ingresso reconstruido na base compartilhada
- suporte e ajuda reconstruidos na base compartilhada
- matriz de paridade web/app executada

**Regra de priorizacao**

- crash e bloqueio de jornada vem antes de feature
- compra e ingresso vem antes de polimento
- suporte claro vem antes de automacao sofisticada

**Criterio de saida**

- jornadas criticas validas em web e app
- sem incidente critico aberto nas jornadas priorizadas

### Fase 4 - Rollout e recuperacao reputacional

**Duracao inicial:** 2 semanas  
**Operacao continua:** apos a liberacao inicial

**Objetivo**

Subir a base nova de forma controlada e acionar recuperacao de reputacao apenas quando houver evidencia de melhora real.

**Entregas**

- rollout interno e controlado
- validacao de links de loja e fluxo de review
- piloto de CX com usuarios elegiveis
- gatilhos eticos de review no produto
- operacao semanal de acompanhamento de reputacao

**Criterio de saida**

- 2 semanas sem incidente critico nas jornadas priorizadas
- playbook de CX validado
- links de loja funcionando em contexto real

---

## 4. Estrategias Operacionais por Frente

### 4.1 Estrategia de Arquitetura

- Uma base de negocio para site e app.
- Uma taxonomia de erro para site e app.
- Uma camada de analytics para site e app.
- Adaptadores minimos por plataforma, revisados caso a caso.
- Nenhuma feature nativa entra no v1 se comprometer simplicidade, velocidade de manutencao ou paridade.

### 4.2 Estrategia de Qualidade

- Primeiro estabilizar, depois promover.
- Crash rate e taxa de sucesso das jornadas sao mais importantes do que volume de entrega.
- Cada release precisa ser validado em:
  - web
  - development build
  - cenarios de timeout
  - retomada de sessao
  - falha conhecida com mensagem compreensivel

### 4.3 Estrategia de Loja e Review

**Android**

- Dentro do app: usar `Google Play In-App Review API`.
- Fora do app, via CX: usar a pagina publica da Play como fallback.
- Nao depender de link externo para abrir formulario direto de avaliacao no Android.

**iOS**

- Dentro do app: usar prompt nativo quando elegivel.
- Fora do app, via CX: usar link persistente com `action=write-review`.

### 4.4 Estrategia de Recuperacao via CX

O time de CX so deve pedir atualizacao de avaliacao quando existir prova de correcao real.

**Elegibilidade**

- usuario reclamou de problema tecnico
- problema foi corrigido
- existe evidencia de uso bem-sucedido apos a correcao

**Exclusoes**

- estorno pendente
- chargeback
- suspeita de fraude
- caso juridico
- ticket encerrado sem resolucao real

**Janela de contato**

- preferencial: `24-72h` depois de uma jornada concluida com sucesso
- fallback: `7-14 dias` apos fechamento manual do caso quando nao houver telemetria

**Cadencia**

- `1` contato principal
- `1` lembrete opcional
- sem terceira tentativa

**Linguagem obrigatoria**

- usar "atualize sua avaliacao"
- nunca usar "deixe 5 estrelas"
- nunca condicionar atendimento a review

---

## 5. Metricas e Criterios de Saida

### 5.1 Metricas primarias

- crash rate
- taxa de sucesso de login
- taxa de sucesso de checkout
- taxa de acesso ao ingresso
- tempo medio de resolucao CX
- paridade web/app nas jornadas criticas

### 5.2 Metricas secundarias

- volume de reviews positivos
- taxa de atualizacao de avaliacao
- rating Google Play
- rating App Store

### 5.3 Gates do programa

**Gate para iniciar campanha de reviews**

- 2 semanas sem incidente critico nas jornadas priorizadas

**Gate para manter rollout**

- nenhuma regressao grave em `login`, `checkout` ou `tickets`

**Gate para reabrir escopo nativo**

- somente depois de o v1 compartilhado estar estavel e medido

---

## 6. Riscos, Premissas e Anexos Operacionais

### 6.1 Riscos principais

- A App Store segue sem baseline operacional em tempo real.
- Android pode continuar sofrendo com churn silencioso por crash sem review.
- Se o time tentar reintroduzir features nativas cedo demais, a base compartilhada perde simplicidade.
- Casos de estorno e litigio continuam impedindo recuperacao de reputacao em parte da base.

### 6.2 Premissas adotadas

- O baseline numerico confiavel atual e o do Google Play em `05-03-2026`.
- "Site e app funcionarem da mesma forma" significa mesma regra de negocio e mesma jornada, nao identidade visual pixel-perfect.
- O v1 prioriza manutencao, previsibilidade e confiabilidade.
- O plano cobre Google Play e App Store, mesmo com maturidade diferente de dados por plataforma.

### 6.3 Links operacionais validados para a estrategia

| Contexto | Plataforma | Link |
|---|---|---|
| CX externo | Android | `https://play.google.com/store/apps/details?id=br.com.quero2ingressos&hl=pt_BR` |
| Device local | Android | `market://details?id=br.com.quero2ingressos` |
| CX externo | iOS | `https://apps.apple.com/br/app/q2-ingressos/id1441533691?action=write-review` |
| Device local | iOS | `itms-apps://itunes.apple.com/app/viewContentsUserReviews/id1441533691?action=write-review` |

### 6.4 Playbook de CX para atualizacao de avaliacao

**Mensagem principal - usuario Android**

> Ola, [nome]. O problema que voce relatou no app Q2 foi corrigido e ja tivemos confirmacao de uso bem-sucedido depois do ajuste. Se fizer sentido para voce, atualize sua avaliacao na loja para refletir sua experiencia atual: https://play.google.com/store/apps/details?id=br.com.quero2ingressos&hl=pt_BR

**Mensagem principal - usuario iOS**

> Ola, [nome]. O problema que voce relatou no app Q2 foi corrigido e ja tivemos confirmacao de uso bem-sucedido depois do ajuste. Se fizer sentido para voce, atualize sua avaliacao na App Store para refletir sua experiencia atual: https://apps.apple.com/br/app/q2-ingressos/id1441533691?action=write-review

**Lembrete**

> Reforcando nosso retorno: o ajuste do problema foi concluido e, se sua experiencia melhorou, voce pode atualizar sua avaliacao quando quiser pelo link abaixo. Obrigado por dar visibilidade ao problema na epoca e por revisar a experiencia atual.

**Checklist antes de disparar**

- ticket resolvido de verdade
- usuario elegivel
- plataforma correta identificada
- link correto inserido
- linguagem sem pedido de nota especifica

### 6.5 Cenarios minimos de teste

- web e app concluem `login` com a mesma regra de negocio
- web e app concluem `checkout` com sucesso e tratam timeout
- web e app exibem `tickets` com fallback e mensagem compreensivel
- web e app abrem `support` sem loop
- Android abre a pagina da Play a partir de WhatsApp/email
- iOS abre a App Store com `write-review`
- gatilho in-app de review nao aparece para usuario com erro aberto

### 6.6 Fontes usadas nesta revisao

- Desk research de App Store / Play Store / Reclame Aqui de `10-12-2025`
- [play-voc-baseline-2026-03-05](C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports\docs\discovery\play-voc-baseline-2026-03-05.md)
- [play-quality-baseline-2026-03-05](C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports\docs\research\play-quality-baseline-2026-03-05.md)
- [Expo development builds](https://docs.expo.dev/develop/development-builds/introduction/)
- [Expo Router](https://docs.expo.dev/router/introduction/)
- [Google Play In-App Reviews API](https://developer.android.com/guide/playcore/in-app-review)
- [Apple RequestReviewAction](https://developer.apple.com/documentation/storekit/requestreviewaction)
- [Q2 Ingressos na App Store](https://apps.apple.com/br/app/q2-ingressos/id1441533691)
- [Q2 Ingressos no Google Play](https://play.google.com/store/apps/details?id=br.com.quero2ingressos&hl=pt_BR)

---

Assinado por: Matheus Ramos - matheus.ramos@q2ingressos.com.br  
Assinado em: 06-03-2026
