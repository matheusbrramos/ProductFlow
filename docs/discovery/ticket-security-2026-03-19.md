# Analise de Discovery - Experiencia de Compra de Ingressos

**Data:** 2026-03-19
**Entrevistas/Reviews:** 6 reviews Play Store (ultimos 30 dias)
**Perfil:** Compradores de ingressos via app Q2 Ingressos
**Confianca:** Baixa (n=6, amostra pequena — recomendo coletar mais dados antes de priorizar)

---

## Jobs-to-be-Done

### Job Principal

**QUANDO** compro um ingresso para um evento pelo app
**QUERO** ter acesso ao meu ingresso de forma confiavel, a qualquer hora e em qualquer condicao
**PARA QUE** eu consiga entrar no evento sem depender de fatores externos (internet, bateria, app funcionando)

Este job e o que esta sendo violado pelos reviews 3, 4 e 5. O usuario nao esta comprando acesso digital gerenciado — ele esta comprando tranquilidade de que conseguira entrar no evento.

### Jobs Secundarios

**Job 2 — Compra sem atrito**
QUANDO decido comprar um ingresso
QUERO concluir a compra com o minimo de passos e bloqueios
PARA QUE o processo nao gere ansiedade nem arrependimento antes mesmo do evento

Evidencia: reviews 1 e 2. O review 1 e particularmente revelador — o usuario se arrepende da compra nao pelo produto (o evento), mas pelo app. Isso e um sinal de que o app esta danificando a percepcao de valor da empresa.

**Job 3 — Backup e contingencia**
QUANDO tenho meu ingresso
QUERO poder salvar uma copia ou ter alternativa offline
PARA QUE eu nao fique sem acesso ao evento por falhas tecnicas, perda de internet ou troca de celular

Evidencia: reviews 3, 4 e 5. O review 5 usa a expressao "empresa anti-imprevisto" — isso nao e so uma reclamacao funcional, e uma percepcao de que a empresa esta contra o usuario em momentos criticos.

**Job 4 — Compartilhamento de ingresso**
QUANDO compro ingressos para acompanhantes
QUERO poder transferir ou compartilhar o ingresso de forma simples
PARA QUE cada pessoa tenha acesso independente ao proprio ingresso

Este job e implicito nos reviews mas nao explicito — merece investigacao adicional em entrevistas qualitativas.

---

## Padroes Identificados

### Critico (4/6 mencionaram — 67%)

**Insight: Ausencia de acesso offline ao ingresso**

Os usuarios percebem a exigencia de internet como uma restricao hostil, nao como uma feature de seguranca. O termo "empresa anti-imprevisto" (review 5) sintetiza a percepcao: a empresa esta design-ando contra o usuario em momentos de vulnerabilidade (sem sinal, bateria fraca, roaming).

O fato de dois reviews terem texto identico (reviews 3 e 4) sugere que outros usuarios leram a reclamacao, se identificaram, e reproduziram — amplificando o sinal.

**Quotes:**
> "Nao permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso." — 1 estrela (x2)

> "Nao permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto." — 1 estrela

> "fala que to sem Internet mas eu tenho Internet. me arrependi" — 1 estrela

### Importante (2/6 mencionaram — 33%)

**Insight: Complexidade e friccao no fluxo de compra**

Dois reviews independentes chegam a conclusao de que o fluxo de compra e excessivamente burocratico. O review 2 usa a palavra "burocracia" — um termo de peso negativo no contexto brasileiro, associado a ineficiencia e obstaculo.

**Quotes:**
> "que app horrivel! tanta burocracia pra comprar um ingresso!" — 1 estrela

> "acabei de comprar um ingresso e tive e que baixar o app e pessimo." — 1 estrela

### Relevante (1/6 mencionaram — 17%)

**Insight: Frustracao difusa sem diagnostico**

O review 6 nao especifica o problema — e raiva generalizada. Isso e relevante porque indica usuarios que tiveram uma experiencia ruim mas nao conseguem (ou nao se dao ao trabalho de) articular o que falhou. Esse grupo silencioso provavelmente e maior do que o que aparece nos reviews.

**Quote:**
> "Aplicativo pessimo, o programador disso deveria ter vergonha" — 1 estrela

---

## Oportunidades

### Oportunidade 1: Ingresso acessivel sem internet (ALTA PRIORIDADE)

**Necessidade nao atendida:** Usuarios precisam acessar o ingresso em condicoes adversas — sem sinal, em roaming, bateria critica, troca de dispositivo.

**Gap atual:** O app exige conexao ativa para renderizar o ingresso. A empresa bloqueia PDF e screenshot por medo de fraude. O resultado e que usuarios legitimos sofrem restricoes pensadas para fraudadores.

**Tensao central a resolver:** Seguranca anti-fraude vs. acesso offline para usuarios legitimos.

Esta tensao e falsa em um nivel tecnico. Existem solucoes que desacoplam os dois objetivos:

- **QR Code com assinatura criptografica e validade temporal** — o codigo e valido por N horas antes do evento, gerado offline apos autenticacao, e invalidado apos uso. Fraudadores nao conseguem replicar porque o codigo muda.
- **Wallet nativo (Google Wallet / Apple Wallet)** — o pass fica no dispositivo, funciona offline, e controlado pela empresa. E o padrao da industria (Ticketmaster, Eventbrite, ingresso.com ja fazem isso).
- **PDF assinado com watermark dinamico** — o PDF contem dados do comprador (nome, CPF mascarado) que inviabiliza transferencia anonima. Quem frauda expoe a propria identidade.

**Impacto estimado:** Alta — 4 dos 6 reviews abordam isso diretamente. Resolve o padrao critico.

**Possiveis solucoes:**
- Integracao com Google Wallet (menor esforco, maior impacto percebido)
- QR Code offline com TTL configuravel por evento
- PDF com watermark personalizado por comprador

---

### Oportunidade 2: Reducao de friccao no fluxo de compra (MEDIA PRIORIDADE)

**Necessidade nao atendida:** Usuarios querem concluir a compra rapidamente, sem obstaculos inesperados.

**Gap atual:** Nao ha dados suficientes para diagnosticar onde exatamente o fluxo falha. O review 1 menciona que teve que "baixar o app" — o que sugere que a jornada de compra pode comecar fora do app (web, link externo) e interrompe o usuario para forcalo a instalar.

**Tensao:** Forcado download vs. conversao — redirecionar para app pode parecer burocracia mesmo sendo intencional.

**Impacto estimado:** Medio — 2 reviews mencionam, mas sem especificidade suficiente para agir sem mais dados.

**Possiveis solucoes:**
- Mapeamento do funil de compra com analytics (onde abandona?)
- Teste A/B: compra via web vs. compra forcada via app
- Reducao de steps no checkout (one-page checkout ou progressive disclosure)

---

### Oportunidade 3: Recuperacao de confianca pos-compra (RELEVANTE)

**Necessidade nao atendida:** Usuarios que tiveram experiencia ruim nao encontram caminho de resolucao — vao direto para o review negativo.

**Gap atual:** Ausencia de suporte proativo ou canal de feedback visivel no app.

**Impacto estimado:** Baixo no curto prazo, mas strategico para reputacao na Play Store.

**Possiveis solucoes:**
- Reply automatico humanizado nos reviews negativos
- In-app feedback antes do usuario sair com frustracao
- Notificacao pos-compra com instrucoes claras de como acessar o ingresso offline

---

## Recomendacoes de Validacao

### Antes de Priorizar Qualquer Solucao

Com apenas 6 reviews, a confianca e **Baixa**. Os padroes sao consistentes mas a amostra e insuficiente para estimar impacto com precisao.

**Acoes recomendadas antes de decidir:**

1. **Entrevistas qualitativas (5-8 usuarios)** — focar em usuarios que compraram ingresso nos ultimos 60 dias. Pergunta-chave: "Me conta sobre a ultima vez que foi a um evento e usou o ingresso digital. O que aconteceu?"

2. **Analytics de funil** — quantos usuarios iniciam a compra e nao concluem? Onde abandonam? Isso valida ou refuta a Oportunidade 2.

3. **Dados de suporte/SAC** — quantos tickets de suporte mencionam "nao consigo acessar ingresso" ou "sem internet"? Isso escala o problema real alem dos reviews.

4. **Benchmarking de solucao offline** — mapear como Ticketmaster, Eventim e ingresso.com resolvem o mesmo problema. Usuarios ja tem expectativa formada por esses players.

### Experimento Sugerido para Oportunidade 1 (Offline Access)

Antes de construir qualquer coisa:
- **Hipotese:** Usuarios abandonam o app ou dao 1 estrela principalmente por nao conseguir acessar o ingresso sem internet.
- **Validacao rapida:** Pesquisa in-app pos-compra (3 perguntas, 30 segundos) perguntando como o usuario pretende usar o ingresso no dia do evento.
- **Criterio de sucesso:** Se 40%+ respondem que precisam de acesso offline, a hipotese e confirmada e justifica investimento.

---

## Proximos Passos Recomendados

1. Validar Oportunidade 1 via pesquisa in-app
2. Integrar Zendesk data para escalar o problema alem dos 6 reviews
3. Criar `/prd` para feature de Offline Access + Anti-Fraud (Google Wallet + QR dinamico)
4. Rodar `/research` para mapear solucoes da concorrencia

---

## Anexo: Todas as Quotes

| Review | Estrelas | Quote | Categoria |
|--------|----------|-------|-----------|
| 1 | 1 | "acabei de comprar um ingresso e tive e que baixar o app e pessimo. fala que to sem Internet mas eu tenho Internet. me arrependi" | Friccao na compra + erro conectividade |
| 2 | 1 | "que app horrivel! tanta burocracia pra comprar um ingresso!" | Complexidade no fluxo |
| 3 | 1 | "Pessimo, nao permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso." | Offline access |
| 4 | 1 | "Pessimo, nao permite exportar o ingresso em PDF nem printar a tela. Exige internet para acessar o ingresso." | Offline access (repetido) |
| 5 | 1 | "Nao permite salvar o ingresso em PDF ou tirar screenshot. Empresa anti-imprevisto." | Offline access + percepcao hostil |
| 6 | 1 | "Aplicativo pessimo, o programador disso deveria ter vergonha" | Frustracao difusa |

---

**Nota sobre confianca:** Esta analise e baseada em 6 reviews — abaixo do minimo recomendado (10+) para conclusoes com confianca media ou alta. Os padroes sao claros e consistentes, mas o escopo quantitativo e a severidade real do problema requerem validacao adicional antes de alocar capacidade de engenharia.

**Criado por:** ProductFlow Discovery Agent + Claude Code
**Data do relatorio:** 2026-03-19
