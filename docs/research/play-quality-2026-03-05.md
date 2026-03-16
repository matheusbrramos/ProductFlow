# Weekly Play Quality Intelligence — 2026-03-05

_Gerado em 2026-03-05T13:48:11.049741+00:00 · Fonte: play_insights.duckdb · Janela: 30 dias_

⚠️ **ALERTA DE POLÍTICA GOOGLE PLAY**

- 🚨 **crashRate:** 25.92% → **23.8x** acima do limite (1.09%) — RISCO CRÍTICO DE DEMOÇÃO

---

## Narrativa da Semana

O app registrou **3 review(s)** nos últimos 30 dias, com média de ⭐ 1.0/5.0 e **100% de avaliações negativas** — tendência **sem dados de tendência suficientes**. O tema que mais concentra insatisfação é **Usabilidade (UX/UI)** (3 relato(s), severidade média 4.0/5). No lado técnico, o crash rate médio foi de **25.92%** — em nível crítico, requer ação imediata. Este relatório consolida o panorama completo para que o time de produto possa tomar decisões informadas sobre onde investir energia na próxima sprint.

---

## Flags de Risco

- 🔴 **Crash rate crítico: 25.92%** (threshold: 5%). App quebrando para mais de 1 em 20 sessões. Prioridade máxima.
- 🔴 **Rating médio abaixo de 3.0 (1.0).** App em risco de receber badge negativo no Play Store. Ação urgente necessária.

---

## Tendência de Rating

| Data | Avg Rating | Reviews | Negativos | Positivos | Tendência |
|------|-----------|---------|-----------|-----------|-----------|
| 2026-03-05 | ⭐ 1.00 | 3 | 3 | 0 | → |

---

## Deep Dive por Categoria — A História de Cada Problema

_Cada categoria é analisada com citações reais, padrões observados e correlação técnica._

### Usabilidade (UX/UI)

**3 relato(s) negativos** · severidade média **4.0/5** · risco: MÉDIA — gera frustração e abandono

> "Péssimo, não permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso."
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "Não permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto."
> _⭐ 1 · en · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "app muito ruim muita burocracia para comprar os ingressos,está pior q banco pede até a cor da sua meia"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

**Recomendação:** Impacto estimado 13.6 · Esforço S · Dono: Product Design

### Experiência de Compra (Ingresso/Ticket)

**3 relato(s) negativos** · severidade média **5.0/5** · risco: —

> "Péssimo, não permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso."
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 5/5 · 3.4.0_

> "Não permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto."
> _⭐ 1 · en · Frustração / Experiência negativa · severidade 5/5 · 3.4.0_

> "app muito ruim muita burocracia para comprar os ingressos,está pior q banco pede até a cor da sua meia"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 5/5 · 3.4.0_

**Palavras-chave:** ingresso, ingressos

**Recomendação:** Impacto estimado 16.9 · Esforço M · Dono: Product + Support

---

## Hotspots Técnicos

### Vitals por Métrica

| Métrica | Média | Pico | Dias com dados | Status |
|---------|-------|------|----------------|--------|
| Crash Rate | 0.2592 (25.92%) | 1.0000 (100.00%) | 13 dias | 🔴 Crítico |
| ANR Rate | 0.0000 (0.00%) | 0.0000 (0.00%) | 13 dias | 🟢 OK |

### Série Temporal do Crash Rate

| Data | Média | Mínimo | Máximo | Segmentos |
|------|-------|--------|--------|-----------|
| 2026-03-03 | 15.05% | 7.02% | 23.08% | 2 |
| 2026-03-02 | 13.86% | 8.62% | 27.59% | 4 |
| 2026-03-01 | 19.39% | 5.77% | 38.00% | 7 |
| 2026-02-28 | 31.37% | 31.37% | 31.37% | 1 |
| 2026-02-27 | 18.64% | 13.85% | 24.07% | 3 |
| 2026-02-14 | 4.55% ⬇️ | 4.55% | 4.55% | 1 |
| 2026-02-09 | 12.56% | 4.35% | 16.67% | 3 |
| 2026-02-08 | 26.21% | 0.00% | 58.33% | 33 |
| 2026-02-07 | 26.56% | 0.00% | 66.67% | 46 |
| 2026-02-06 | 30.22% | 0.00% | 100.00% | 39 |
| 2026-02-05 | 35.57% ⬆️ | 13.33% | 100.00% | 9 |
| 2026-02-04 | 11.15% | 0.00% | 26.67% | 6 |
| 2026-02-03 | 22.22% | 0.00% | 50.00% | 3 |

> **Pior dia:** 2026-02-05 — média 35.57%, pico 100.00%
> **Melhor dia:** 2026-02-14 — média 4.55%

### Dispositivos Mais Afetados pelos Crashes

| Dispositivo | Android | Versão app | Crash Rate Médio | Dias |
|-------------|---------|-----------|-----------------|------|
| samsung/a25x | API 36 | 20252 | 57.1% | 1d |
| motorola/lamul | API 35 | 20252 | 55.1% | 1d |
| motorola/lamu | API 35 | 20252 | 51.6% | 3d |
| samsung/r0q | API 36 | 20252 | 50.0% | 1d |
| motorola/manila | API 34 | 20252 | 49.7% | 3d |
| samsung/r12s | API 36 | 20252 | 48.4% | 4d |
| samsung/a35x | API 36 | 20252 | 47.7% | 3d |
| samsung/a15x | API 36 | 20252 | 45.7% | 3d |
| Redmi/fire | API 35 | 20252 | 41.3% | 2d |
| motorola/rhode | API 33 | 20252 | 40.4% | 1d |

> **Maior offender:** `samsung/a25x` (Android API 36) — 57.1% de crash rate médio. Priorizar investigação neste dispositivo.

### Disponibilidade de Dados de Crash — O Que Temos e O Que Falta

**530 segmentos de crash rate** coletados na base de dados.

| Dimensão | Com dados | Sem dados | Impacto |
|----------|-----------|-----------|---------|
| Versão do app | 530 | 0 | ✅ Pode-se ver quais versões crasham mais |
| Modelo de dispositivo | 530 | 0 | ✅ Pode-se ver quais dispositivos crasham mais |
| País | 530 | 0 | ✅ Pode-se ver regiões mais afetadas |

> **Error Issues API:** 0 registros retornados no período. Stack traces e erros específicos não estão disponíveis via esta API. Consultar Firebase Crashlytics ou Play Console diretamente.

---

## Diagnóstico de Crashes — 🔴 CRÍTICO

### Para Stakeholders — O Que Está Acontecendo

O app está travando principalmente em usuários com **Android 14 e Android 15 e Android 16 (preview)**. Isso indica que uma atualização recente do sistema operacional mudou alguma regra que o app ainda não está preparado para seguir. É como se o governo publicasse uma nova lei de trânsito e o GPS do carro ainda não soubesse das mudanças — o app não sabe como se comportar nesse novo ambiente.

> **Impacto estimado no negócio:** A cada **4 tentativas de abrir o app**, **1 termina com o app fechando sozinho**. Se o app tem 10.000 sessões diárias, aproximadamente **2,592 usuários por dia** não conseguem usar o app. Cada crash = usuário que potencialmente abandona a compra, deixa avaliação negativa ou desinstala o app.

O modelo mais afetado é **samsung/a25x** (Android 16 (preview)) com **57%** de crash — ou seja, 57 em cada 100 sessões nesse aparelho travam.  
A versão ativa **20252** tem crash rate médio de **25.9%**.

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
| 20252 | 25.9% | 13d | 2026-02-03 → 2026-03-03 |

---

## Problemas Persistentes — Quanto Tempo Cada Categoria Está Presente

| Categoria | Presente desde | Semanas | Reviews | Status |
|-----------|---------------|---------|---------|--------|
| Usabilidade (UX/UI) | 2026-03-04 | 1 sem. | 3 | 🟠 Novo |
| Experiência de Compra (Ingresso/Ticket) | 2026-03-05 | 1 sem. | 3 | 🟠 Novo |

---

## Correlação: Crash Rate × Reviews Negativos por Semana

| Semana | Crash Rate | Reviews Negativos |
|--------|------------|------------------|
| 2026-03-02 | 14.3% | 3 |
| 2026-02-23 | 20.3% | 0 |
| 2026-02-09 | 10.6% | 0 |
| 2026-02-02 | 27.3% | 0 |

> Semanas com crash >20% concentram **0%** dos reviews negativos do período.

---

## Matriz de Impacto — Onde Focar

Cada categoria é posicionada por **volume de queixas** (eixo X) e **severidade média** (eixo Y). Priorize o quadrante superior direito.

|  | **Volume Alto** | **Volume Baixo** |
|--|-----------------|-----------------|
| **Severidade Alta** | 🔴 Atacar agora<br>Usabilidade (UX/UI) (3 · sev 4.0)<br>Experiência de Compra (Ingresso/Ticket) (3 · sev 5.0) | 🟡 Investigar<br>— |
| **Severidade Baixa** | 🟡 Planejar<br>— | 🟢 Monitorar<br>— |

---

## Roadmap Estratégico — Prioridades para a Próxima Sprint

_Lista curada ordenada por impacto esperado. Combina evidências de reviews, vitals e issues._

#### 1. Experiência de Compra (Ingresso/Ticket)
**Impacto:** 16.9 | **Esforço:** M | **Dono:** Product + Support | **Risco:** —

**Evidência consolidada:** 3 review(s) negativo(s) · severidade média 5.00/5 · vitals 12.96%

#### 2. Usabilidade (UX/UI)
**Impacto:** 13.6 | **Esforço:** S | **Dono:** Product Design | **Risco:** MÉDIA — gera frustração e abandono

**Evidência consolidada:** 3 review(s) negativo(s) · severidade média 4.00/5 · vitals 12.96%

---

_Relatório semanal gerado em 2026-03-05T13:48:11.049741+00:00_
