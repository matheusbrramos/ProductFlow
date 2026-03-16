# Weekly Play Quality Intelligence — 2026-03-09

_Gerado em 2026-03-09T11:29:39.339462+00:00 · Fonte: play_insights.duckdb · Janela: 30 dias_

⚠️ **ALERTA DE POLÍTICA GOOGLE PLAY**

- 🚨 **crashRate:** 25.50% → **23.4x** acima do limite (1.09%) — RISCO CRÍTICO DE DEMOÇÃO

---

## Narrativa da Semana

O app registrou **4 review(s)** nos últimos 30 dias, com média de ⭐ 1.0/5.0 e **100% de avaliações negativas** — tendência **estável**. O tema que mais concentra insatisfação é **Usabilidade (UX/UI)** (4 relato(s), severidade média 4.0/5). No lado técnico, o crash rate médio foi de **25.50%** — em nível crítico, requer ação imediata. Este relatório consolida o panorama completo para que o time de produto possa tomar decisões informadas sobre onde investir energia na próxima sprint.

---

## Flags de Risco

- 🔴 **Crash rate crítico: 25.50%** (threshold: 5%). App quebrando para mais de 1 em 20 sessões. Prioridade máxima.
- 🔴 **Rating médio abaixo de 3.0 (1.0).** App em risco de receber badge negativo no Play Store. Ação urgente necessária.

---

## Tendência de Rating

| Data | Avg Rating | Reviews | Negativos | Positivos | Tendência |
|------|-----------|---------|-----------|-----------|-----------|
| 2026-03-05 | ⭐ 1.00 | 2 | 2 | 0 | → |
| 2026-03-09 | ⭐ 1.00 | 2 | 2 | 0 | → |

---

## Deep Dive por Categoria — A História de Cada Problema

_Cada categoria é analisada com citações reais, padrões observados e correlação técnica._

### Usabilidade (UX/UI)

**4 relato(s) negativos** · severidade média **4.0/5** · risco: MÉDIA — gera frustração e abandono

> "Aplicativo péssimo, o programador disso deveria ter vergonha"
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "Péssimo, não permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso."
> _⭐ 1 · pt · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

> "Não permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto."
> _⭐ 1 · en · Frustração / Experiência negativa · severidade 4/5 · 3.4.0_

**Recomendação:** Impacto estimado 18.0 · Esforço S · Dono: Product Design

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
| Crash Rate | 0.2550 (25.50%) | 0.6667 (66.67%) | 13 dias | 🔴 Crítico |
| ANR Rate | 0.0000 (0.00%) | 0.0000 (0.00%) | 13 dias | 🟢 OK |

### Série Temporal do Crash Rate

| Data | Média | Mínimo | Máximo | Segmentos |
|------|-------|--------|--------|-----------|
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
| 2026-02-09 | 12.56% | 4.35% | 16.67% | 3 |
| 2026-02-08 | 26.21% | 0.00% | 58.33% | 33 |
| 2026-02-07 | 26.56% | 0.00% | 66.67% | 46 |

> **Pior dia:** 2026-03-06 — média 32.22%, pico 57.14%
> **Melhor dia:** 2026-02-14 — média 4.55%

### Dispositivos Mais Afetados pelos Crashes

| Dispositivo | Android | Versão app | Crash Rate Médio | Dias |
|-------------|---------|-----------|-----------------|------|
| samsung/a25x | API 36 | 20252 | 57.1% | 1d |
| motorola/manila | API 35 | 20252 | 56.6% | 2d |
| samsung/a15x | API 36 | 20252 | 51.1% | 3d |
| Redmi/fire | API 35 | 20252 | 50.0% | 1d |
| samsung/r0q | API 36 | 20252 | 50.0% | 1d |
| samsung/a06 | API 36 | 20252 | 49.0% | 1d |
| motorola/manila | API 34 | 20252 | 48.0% | 2d |
| motorola/lamu | API 35 | 20252 | 48.0% | 3d |
| samsung/a36xq | API 36 | 20252 | 46.0% | 1d |
| samsung/r11s | API 36 | 20252 | 45.7% | 4d |

> **Maior offender:** `samsung/a25x` (Android API 36) — 57.1% de crash rate médio. Priorizar investigação neste dispositivo.

### Disponibilidade de Dados de Crash — O Que Temos e O Que Falta

**596 segmentos de crash rate** coletados na base de dados.

| Dimensão | Com dados | Sem dados | Impacto |
|----------|-----------|-----------|---------|
| Versão do app | 596 | 0 | ✅ Pode-se ver quais versões crasham mais |
| Modelo de dispositivo | 596 | 0 | ✅ Pode-se ver quais dispositivos crasham mais |
| País | 596 | 0 | ✅ Pode-se ver regiões mais afetadas |

> **Error Issues API:** 0 registros retornados no período. Stack traces e erros específicos não estão disponíveis via esta API. Consultar Firebase Crashlytics ou Play Console diretamente.

---

## Diagnóstico de Crashes — 🔴 CRÍTICO

### Para Stakeholders — O Que Está Acontecendo

O app está travando principalmente em usuários com **Android 14 e Android 15 e Android 16 (preview)**. Isso indica que uma atualização recente do sistema operacional mudou alguma regra que o app ainda não está preparado para seguir. É como se o governo publicasse uma nova lei de trânsito e o GPS do carro ainda não soubesse das mudanças — o app não sabe como se comportar nesse novo ambiente.

> **Impacto estimado no negócio:** A cada **4 tentativas de abrir o app**, **1 termina com o app fechando sozinho**. Se o app tem 10.000 sessões diárias, aproximadamente **2,549 usuários por dia** não conseguem usar o app. Cada crash = usuário que potencialmente abandona a compra, deixa avaliação negativa ou desinstala o app.

O modelo mais afetado é **samsung/a25x** (Android 16 (preview)) com **57%** de crash — ou seja, 57 em cada 100 sessões nesse aparelho travam.  
A versão ativa **20252** tem crash rate médio de **25.5%**.

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
| 20252 | 25.5% | 13d | 2026-02-07 → 2026-03-07 |

---

## Problemas Persistentes — Quanto Tempo Cada Categoria Está Presente

| Categoria | Presente desde | Semanas | Reviews | Status |
|-----------|---------------|---------|---------|--------|
| Usabilidade (UX/UI) | 2026-03-04 | 2 sem. | 4 | 🟡 Recorrente |
| Experiência de Compra (Ingresso/Ticket) | 2026-03-09 | 1 sem. | 3 | 🟠 Novo |

---

## Correlação: Crash Rate × Reviews Negativos por Semana

| Semana | Crash Rate | Reviews Negativos |
|--------|------------|------------------|
| 2026-03-02 | 26.1% | 3 |
| 2026-02-23 | 20.3% | 0 |
| 2026-02-09 | 10.6% | 0 |
| 2026-02-02 | 26.4% | 0 |

> Semanas com crash >20% concentram **100%** dos reviews negativos do período.

---

## Matriz de Impacto — Onde Focar

Cada categoria é posicionada por **volume de queixas** (eixo X) e **severidade média** (eixo Y). Priorize o quadrante superior direito.

|  | **Volume Alto** | **Volume Baixo** |
|--|-----------------|-----------------|
| **Severidade Alta** | 🔴 Atacar agora<br>Usabilidade (UX/UI) (4 · sev 4.0) | 🟡 Investigar<br>Experiência de Compra (Ingresso/Ticket) (3 · sev 5.0) |
| **Severidade Baixa** | 🟡 Planejar<br>— | 🟢 Monitorar<br>— |

---

## Roadmap Estratégico — Prioridades para a Próxima Sprint

_Lista curada ordenada por impacto esperado. Combina evidências de reviews, vitals e issues._

#### 1. Usabilidade (UX/UI)
**Impacto:** 18.0 | **Esforço:** S | **Dono:** Product Design | **Risco:** MÉDIA — gera frustração e abandono

**Evidência consolidada:** 4 review(s) negativo(s) · severidade média 4.00/5 · vitals 12.75%

#### 2. Experiência de Compra (Ingresso/Ticket)
**Impacto:** 16.9 | **Esforço:** M | **Dono:** Product + Support | **Risco:** —

**Evidência consolidada:** 3 review(s) negativo(s) · severidade média 5.00/5 · vitals 12.75%

---

_Relatório semanal gerado em 2026-03-09T11:29:39.339462+00:00_
