# Weekly Play Quality Intelligence — 2026-03-16

_Gerado em 2026-03-16T14:57:01.473046+00:00 · Fonte: C:\Users\matheus.santos_q2ing\AppData\Local\play_insights\play_insights.duckdb · Janela: 30 dias_

⚠️ **ALERTA DE POLÍTICA GOOGLE PLAY**

- 🚨 **crashRate:** 22.72% → **20.8x** acima do limite (1.09%) — RISCO CRÍTICO DE DEMOÇÃO

---

## Narrativa da Semana

O app registrou **6 review(s)** nos últimos 30 dias, com média de ⭐ 1.0/5.0 e **100% de avaliações negativas** — tendência **estável**. O tema que mais concentra insatisfação é **Experiência de Compra (Ingresso/Ticket)** (5 relato(s), severidade média 5.0/5). No lado técnico, o crash rate médio foi de **22.72%** — em nível crítico, requer ação imediata. Este relatório consolida o panorama completo para que o time de produto possa tomar decisões informadas sobre onde investir energia na próxima sprint.

---

## Flags de Risco

- 🔴 **Crash rate crítico: 22.72%** (threshold: 5%). App quebrando para mais de 1 em 20 sessões. Prioridade máxima.
- 🔴 **Rating médio abaixo de 3.0 (1.0).** App em risco de receber badge negativo no Play Store. Ação urgente necessária.

---

## Tendência de Rating

| Data | Avg Rating | Reviews | Negativos | Positivos | Tendência |
|------|-----------|---------|-----------|-----------|-----------|
| 2026-03-05 | ⭐ 1.00 | 2 | 2 | 0 | → |
| 2026-03-09 | ⭐ 1.00 | 2 | 2 | 0 | → |
| 2026-03-16 | ⭐ 1.00 | 2 | 2 | 0 | → |

> **Interpretação:** Rating estável no período. Nenhuma melhoria ou piora significativa detectada.

---

## Deep Dive por Categoria — A História de Cada Problema

_Cada categoria é analisada com citações reais, padrões observados e correlação técnica._

### Experiência de Compra (Ingresso/Ticket)

**5 relato(s) negativos** · severidade média **5.0/5** · risco: —

> "acabei de comprar um ingresso e tive e que baixar o app é péssimo. fala que to sem Internet mas eu tenho Internet. me arrependi"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 5/5 · versão não identificada_

> "que app horrível! tanta burocracia pra comprar um ingresso!"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 5/5 · 3.4.0_

> "Péssimo, não permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso."
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 5/5 · 3.4.0_

**Palavras-chave:** ingresso, ingressos

**Recomendação:** Impacto estimado 27.8 · Esforço M · Dono: Product + Support

### Usabilidade (UX/UI)

**4 relato(s) negativos** · severidade média **4.0/5** · risco: MÉDIA — gera frustração e abandono

> "Aplicativo péssimo, o programador disso deveria ter vergonha"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "Péssimo, não permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso."
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "Não permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto."
> _⭐ 1 · en · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

**Recomendação:** Impacto estimado 17.8 · Esforço S · Dono: Product Design

---

## Hotspots Técnicos

### Vitals por Métrica

| Métrica | Média | Pico | Dias com dados | Status |
|---------|-------|------|----------------|--------|
| Crash Rate | 0.2272 (22.72%) | 0.5714 (57.14%) | 17 dias | 🔴 Crítico |
| ANR Rate | 0.0000 (0.00%) | 0.0000 (0.00%) | 17 dias | 🟢 OK |

### Série Temporal do Crash Rate

| Data | Média | Mínimo | Máximo | Segmentos |
|------|-------|--------|--------|-----------|
| 2026-03-14 | 27.01% | 6.12% | 49.12% | 29 |
| 2026-03-13 | 17.84% | 5.97% | 31.37% | 16 |
| 2026-03-12 | 17.38% | 7.14% | 35.94% | 10 |
| 2026-03-11 | 16.09% | 1.41% | 28.36% | 12 |
| 2026-03-10 | 14.83% | 7.27% | 28.00% | 6 |
| 2026-03-09 | 17.45% | 0.00% | 30.19% | 10 |
| 2026-03-08 | 21.33% | 5.56% | 38.00% | 9 |
| 2026-03-07 | 20.22% | 0.00% | 33.87% | 11 |
| 2026-03-06 | 32.22% ⬆️ | 10.98% | 57.14% | 32 |
| 2026-03-05 | 24.49% | 7.35% | 56.00% | 20 |
| 2026-03-04 | 17.18% | 7.02% | 24.53% | 3 |
| 2026-03-03 | 15.05% | 7.02% | 23.08% | 2 |
| 2026-03-02 | 13.86% | 8.62% | 27.59% | 4 |
| 2026-03-01 | 19.39% | 5.77% | 38.00% | 7 |
| 2026-02-28 | 31.37% | 31.37% | 31.37% | 1 |
| 2026-02-27 | 18.64% | 13.85% | 24.07% | 3 |
| 2026-02-14 | 4.55% ⬇️ | 4.55% | 4.55% | 1 |

> **Pior dia:** 2026-03-06 — média 32.22%, pico 57.14%
> **Melhor dia:** 2026-02-14 — média 4.55%

### Dispositivos Mais Afetados pelos Crashes

| Dispositivo | Android | Versão app | Crash Rate Médio | Dias |
|-------------|---------|-----------|-----------------|------|
| motorola/manila | API 35 | 20252 | 54.1% | 3d |
| samsung/a06 | API 36 | 20252 | 49.0% | 1d |
| samsung/a36xq | API 36 | 20252 | 46.0% | 1d |
| samsung/a34x | API 36 | 20252 | 44.1% | 1d |
| samsung/a15x | API 36 | 20252 | 43.0% | 2d |
| samsung/a35x | API 36 | 20252 | 42.7% | 3d |
| motorola/lamu | API 35 | 20252 | 42.6% | 2d |
| motorola/penang | API 34 | 20252 | 41.9% | 2d |
| samsung/a32 | API 33 | 20252 | 37.7% | 2d |
| samsung/r11s | API 36 | 20252 | 37.7% | 5d |

> **Maior offender:** `motorola/manila` (Android API 35) — 54.1% de crash rate médio. Priorizar investigação neste dispositivo.

### Disponibilidade de Dados de Crash — O Que Temos e O Que Falta

**688 segmentos de crash rate** coletados na base de dados.

| Dimensão | Com dados | Sem dados | Impacto |
|----------|-----------|-----------|---------|
| Versão do app | 688 | 0 | ✅ Pode-se ver quais versões crasham mais |
| Modelo de dispositivo | 688 | 0 | ✅ Pode-se ver quais dispositivos crasham mais |
| País | 688 | 0 | ✅ Pode-se ver regiões mais afetadas |

> **Error Issues API:** 0 registros retornados no período. Stack traces e erros específicos não estão disponíveis via esta API. Consultar Firebase Crashlytics ou Play Console diretamente.

---

## Diagnóstico de Crashes — 🔴 CRÍTICO

### Para Stakeholders — O Que Está Acontecendo

O app está travando principalmente em usuários com **Android 14 e Android 15 e Android 16 (preview)**. Isso indica que uma atualização recente do sistema operacional mudou alguma regra que o app ainda não está preparado para seguir. É como se o governo publicasse uma nova lei de trânsito e o GPS do carro ainda não soubesse das mudanças — o app não sabe como se comportar nesse novo ambiente.

> **Impacto estimado no negócio:** A cada **4 tentativas de abrir o app**, **1 termina com o app fechando sozinho**. Se o app tem 10.000 sessões diárias, aproximadamente **2,272 usuários por dia** não conseguem usar o app. Cada crash = usuário que potencialmente abandona a compra, deixa avaliação negativa ou desinstala o app.

O modelo mais afetado é **motorola/manila** (Android 15) com **54%** de crash — ou seja, 54 em cada 100 sessões nesse aparelho travam.  
A versão ativa **20252** tem crash rate médio de **22.7%**.

### Para o Time de Desenvolvimento — Onde Investigar

**Padrão detectado:** Incompatibilidade com versão recente do Android. APIs obsoletas, mudanças de ciclo de vida de Activity/Fragment, novas restrições de permissão ou comportamento alterado de intents.

**Próximos passos recomendados (em ordem de prioridade):**

1. Reproduzir em emulador Android 15 (API 35) — criar um emulador Pixel com API 35 no AVD Manager
2. Verificar `targetSdkVersion` e `compileSdkVersion` no `build.gradle` — atualizar para 35 se necessário
3. Revisar uso de APIs deprecated no Android 14/15: `onBackPressed()`, `startActivityForResult()`, intents com flags restritas
4. Checar mudanças de ciclo de vida: Android 15 alterou comportamento de `Activity` em modo PiP e split-screen
5. Verificar permissões: Android 14+ exige declaração explícita de `FOREGROUND_SERVICE_TYPE`
6. Filtrar crashes no Play Console por Android API 35 e ver o stack trace completo com `Caused by:`
7. Integrar Firebase Crashlytics se não ativo — captura stack traces completos em tempo real

---

## Performance de UI e Startup

_Dados de rendering/startup ainda não coletados._

---

## Análise por Versão do App

| Versão | Crash Rate Médio | Dias | Período |
|--------|-----------------|------|---------|
| 20252 | 22.7% | 17d | 2026-02-14 → 2026-03-14 |

---

## Problemas Persistentes — Quanto Tempo Cada Categoria Está Presente

| Categoria | Presente desde | Semanas | Reviews | Status |
|-----------|---------------|---------|---------|--------|
| Usabilidade (UX/UI) | 2026-03-04 | 2 sem. | 4 | 🟡 Recorrente |
| Experiência de Compra (Ingresso/Ticket) | 2026-03-16 | 1 sem. | 5 | 🟠 Novo |

---

## Correlação: Crash Rate × Reviews Negativos por Semana

| Semana | Crash Rate | Reviews Negativos |
|--------|------------|------------------|
| 2026-03-09 | 20.5% | 0 |
| 2026-03-02 | 25.6% | 3 |
| 2026-02-23 | 20.3% | 0 |
| 2026-02-09 | 4.6% | 0 |

> Semanas com crash >20% concentram **100%** dos reviews negativos do período.

---

## Matriz de Impacto — Onde Focar

Cada categoria é posicionada por **volume de queixas** (eixo X) e **severidade média** (eixo Y). Priorize o quadrante superior direito.

|  | **Volume Alto** | **Volume Baixo** |
|--|-----------------|-----------------|
| **Severidade Alta** | 🔴 Atacar agora<br>Experiência de Compra (Ingresso/Ticket) (5 · sev 5.0) | 🟡 Investigar<br>Usabilidade (UX/UI) (4 · sev 4.0) |
| **Severidade Baixa** | 🟡 Planejar<br>— | 🟢 Monitorar<br>— |

---

## Roadmap Estratégico — Prioridades para a Próxima Sprint

_Lista curada ordenada por impacto esperado. Combina evidências de reviews, vitals e issues._

#### 1. Experiência de Compra (Ingresso/Ticket)
**Impacto:** 27.8 | **Esforço:** M | **Dono:** Product + Support | **Risco:** —

**Evidência consolidada:** 5 review(s) negativo(s) · severidade média 5.00/5 · vitals 11.36%

#### 2. Usabilidade (UX/UI)
**Impacto:** 17.8 | **Esforço:** S | **Dono:** Product Design | **Risco:** MÉDIA — gera frustração e abandono

**Evidência consolidada:** 4 review(s) negativo(s) · severidade média 4.00/5 · vitals 11.36%

---

_Relatório semanal gerado em 2026-03-16T14:57:01.473046+00:00_
