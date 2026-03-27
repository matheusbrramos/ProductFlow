# Pesquisa de Mercado: Acesso Offline, Anti-Fraude e Transferencia de Ingressos

**Gerado em:** 2026-03-19
**Analista:** /researcher (ProductFlow)
**Escopo:** Ticketmaster, Eventbrite, ingresso.com, Sympla, StubHub, Eventim (BR e global)
**Contexto:** Q2 Ingressos - resolver tensao entre acesso offline do usuario vs. controle anti-fraude

---

## Sumario Executivo

### Visao Geral do Mercado

O setor de ticketing digital convergiu para um padrao claro em 2024-2025: QR code dinamico + carteira digital como mecanismo central de acesso offline seguro. A industria abandonou o PDF estatico como veiculo de acesso ao evento - nao porque e impossivel, mas porque cria vetor de fraude incontrolavel. A solucao que o mercado encontrou nao foi bloquear tudo, mas mover o ativo de seguranca para dentro do app e da carteira, tornando o PDF um documento auxiliar (nao de acesso).

No Brasil, Eventim e Sympla ja implementaram mecanismos onde o QR fica em branco ao tentar tirar screenshot ou o codigo so e liberado horas antes do evento. O Q2 Ingressos esta na mesma posicao que o mercado global estava em 2018-2019 (pre-SafeTix) e tem a oportunidade de pular para o padrao atual sem precisar inventar nada.
### Ranking de Players por Maturidade Tecnica

| Posicao | Player | Maturidade | Principal Diferencial |
|---------|--------|------------|-----------------------|
| 1 | Ticketmaster | Alta | SafeTix TOTP - padrao global |
| 2 | Eventim (global) | Alta | PDF + Wallet + Eventim.Pass com QR bloqueado |
| 3 | Eventim Brasil | Media-Alta | Eventim.Pass com screenshot bloqueado |
| 4 | Sympla | Media | QR liberado 4h antes, offline no app |
| 5 | ingresso.com | Media | Wallet via Google/Apple, sem PDF de acesso |
| 6 | Eventbrite | Media | Wallet + QR estatico - menor protecao |
| 7 | StubHub | Media | Garantia financeira, nao tecnica |
| 8 | Q2 Ingressos | Baixa | Bloqueia tudo, zero alternativa offline |

### Principais Insights

1. Nenhum grande player bloqueia acesso sem oferecer alternativa viavel offline - o Q2 e outlier negativo.
2. QR code dinamico e o padrao global - Ticketmaster usa desde 2019 (SafeTix), Eventim BR implementou versao local.
3. Apple Wallet e Google Wallet resolvem offline - funcionam sem internet apos sincronizacao previa.
4. PDF pode coexistir com seguranca - Eventim Europa oferece PDF + Wallet + Eventim.Pass por tipo de evento.
5. Transferencia controlada e feature, nao risco - Sympla, Eventim BR e ingresso.com permitem transferencia com auditoria.

---

## Analise Detalhada por Player

---

### 1. Ticketmaster
test append

**Sede:** Los Angeles, EUA | **Fundacao:** 1976 | **Porte:** Maior ticketadora do mundo (Live Nation Entertainment)
**Mercados:** EUA, Reino Unido, Australia, Canada, Europa - nao opera diretamente no Brasil

**Acesso Offline:** Tickets nao podem ser baixados como PDF nem impressos. Estrategia oficial: adicione a carteira digital antes de sair para o evento. Apple Wallet e Google Wallet funcionam offline apos sincronizacao.

**QR Code - SafeTix:** Sistema proprietario lancado em 2019. Tecnologia: barcode PDF417 com TOTP (Time-based One-Time Password) - a mesma usada em autenticadores 2FA. O QR code se renova a cada 15 segundos. Existe uma chave por cliente e uma chave por ingresso derivadas de servidores Ticketmaster. O algoritmo foi objeto de engenharia reversa publicada em 2024 (conduition.io), mas a protecao pratica permanece eficaz pois exige sincronizacao de relogio com servidor.

**PDF:** Explicitamente bloqueado para eventos SafeTix.

**Apple Wallet / Google Wallet:** Suporte nativo com botao dedicado no app e no browser mobile.

**Transferencia:** Permitida dentro do ecossistema. Apos transferencia, o QR original e invalidado e um novo e gerado para o receptor.

**Pontos Fortes:** SafeTix e o padrao tecnico mais avancado do mercado; Wallet integration elimina dependencia de internet; Transferencia auditada invalida QR anterior.

**Pontos Fracos:** Exige app ou browser sem fallback; Reclamacoes sobre Apple Wallet falhando fora dos EUA; Nao opera no Brasil diretamente.

**Presenca Digital:** App Store 4.8/5 (EUA), Play Store 4.6/5 (EUA).

---

### 2. Eventbrite

**Sede:** San Francisco, EUA | **Fundacao:** 2006 | **Porte:** ~50 milhoes de ingressos/ano

**Acesso Offline:** iOS e Android permitem salvar ticket como imagem diretamente pelo app. Desde marco de 2024, PDFs nao sao mais enviados automaticamente por e-mail. PDF ainda acessivel via login no site.

**QR Code:** Estatico - nao rotativo. Screenshots funcionam tecnicamente. Sem protecao equivalente ao SafeTix.

**Apple Wallet / Google Wallet:** Suportado, mas com inconsistencias reportadas por usuarios.

**Transferencia:** Cada organizador define a politica. Sem transferencia formal com auditoria por padrao.

**Pontos Fortes:** Fluxo simples para organizadores; Imagem offline e solucao pratica mesmo sem sofisticacao.

**Pontos Fracos:** QR estatico e vulneravel a screenshots; Wallet inconsistente por evento; Sem transferencia auditada por padrao.

---

### 3. ingresso.com

**Sede:** Sao Paulo, Brasil | **Fundacao:** 1999 | **Foco:** Cinema (Cinemark, Kinoplex, Cinepolis, UCI), shows e eventos ao vivo

**Acesso Offline:** Ingressos armazenados no Google Wallet (Android) ou Apple Wallet (iOS). Apos download, a carteira funciona offline. Para Rock in Rio 2022, o sistema era exclusivamente via carteira digital - sem PDF, sem print.

**QR Code:** Suporte a NFC e QR Code. Prints ou copias impressas nao sao validos. Se o QR e dinamico ou estatico nao foi confirmado em fontes publicas. [REQUER VERIFICACAO ADICIONAL]

**PDF:** Bloqueado como documento de acesso. PDFs existem apenas como comprovante de compra no e-mail.

**Apple Wallet / Google Wallet:** Suporte nativo. iOS acessa via NFC. Android via NFC ou QR Code.

**Transferencia:** Permitida uma vez. Prazo de 24h para aceitar. Ingresso recebido nao pode ser retransferido.

**Pontos Fortes:** Integracao solida com Apple/Google Wallet; NFC acelera entrada em grandes eventos; Transferencia com regras claras.

**Pontos Fracos:** Informacao publica insuficiente sobre QR dinamico vs. estatico; Usuarios que trocam de SO precisam de suporte manual.

---

### 4. Sympla

**Sede:** Belo Horizonte, Brasil | **Fundacao:** 2012 | **Foco:** Eventos de todos os portes

**Acesso Offline:** O app Sympla armazena ingressos localmente. Mesmo offline, o ingresso aparece na aba Ingressos do app. Confirmado na documentacao oficial.

**QR Code - Liberacao com antecedencia:** Para eventos com maior protecao, o QR Code e gerado 4 horas antes do inicio do evento. Apos geracao, o codigo dura 15 minutos. Reduz janela de fraude por screenshots.

**PDF:** Disponivel para a maioria dos eventos. Para eventos selecionados (configuracao do organizador), ticket fica apenas no app. Plataforma em transicao do modelo PDF para app-only.

**Apple Wallet / Google Wallet:** Sem integracao nativa consolidada. O app Sympla serve como carteira proprietaria.

**Transferencia:** Via app e web. Prazo: ate 24h antes do evento. Limitacao padrao: 1 transferencia por ingresso.

**Pontos Fortes:** Transferencia de titularidade bem documentada; QR com liberacao tardia reduz fraude sem bloquear acesso; Offline confirmado via app; Produtor tem controle granular (PDF ou app-only).

**Pontos Fracos:** Sem integracao com Apple/Google Wallet nativo; QR de 15 minutos pode gerar ansiedade na fila; Reclamacoes de ingresso nao aparecendo no app logo apos compra.

---

### 5. StubHub

**Sede:** San Francisco, EUA | **Fundacao:** 2000 | **Modelo:** Marketplace de revenda - nao emite ingressos originais

**Entrega de ingresso:** (1) Mobile Transfer via app de origem; (2) E-ticket PDF; (3) Mobile Tickets em apps proprietarios.

**Acesso Offline:** Apos receber o Mobile Transfer, comprador pode adicionar a Apple Wallet ou Google Wallet.

**Anti-Fraude - FanProtect:** Mecanismo financeiro-contratual (nao tecnico). Se o ingresso for invalido, StubHub reembolsa ou fornece ingresso equivalente. Sellers com ingressos invalidos sao cobrados 100% do valor + custos. O BBB dos EUA da nota F ao StubHub por fraudes que FanProtect nao conseguiu prevenir tecnicamente.

**Pontos Fortes:** FanProtect oferece protecao financeira ao comprador; Suporte a multiplos formatos.

**Pontos Fracos:** Sem protecao tecnica de QR dinamico; Fraude documentada - nota F no BBB dos EUA; Modelo de revenda cria incentivo estrutural para fraude.

---

### 6. Eventim (Global + Brasil)

**Sede:** Bremen, Alemanha | **Fundacao:** 1996 | **Porte:** Maior ticketadora da Europa; opera no Brasil como Eventim Brasil

**Formatos de ingresso (Europa):** (1) PDF imprimivel; (2) Mobile ticket via app ou Wallet; (3) Eventim.Pass - ticket exclusivo no app com QR bloqueado.

**Acesso Offline:** Eventim.Pass visivel por ate 7 dias apos o evento, com acesso offline desde que o app tenha sido aberto ao menos uma vez.

**Eventim.Pass Brasil - Destaque no mercado brasileiro:**
- Ingresso existe exclusivamente no app
- QR Code fica em branco quando usuario tenta tirar screenshot (mecanismo tecnico confirmado pela empresa)
- QR liberado apenas dias antes do evento (just-in-time)
- Transferencia permitida uma vez dentro do app, entre contas Eventim
- Transferencia bloqueada no dia do evento
- Acesso offline confirmado: funciona sem internet se o app foi aberto ao menos uma vez

**PDF (Brasil):** Para eventos sem Eventim.Pass, PDF e enviado normalmente. Para eventos com Eventim.Pass, PDF nao existe.

**Apple Wallet / Google Wallet:** Europa: suportado. Brasil (Eventim.Pass): nao suportado na Wallet do SO.

**Transferencia:** Dentro do app, uma transferencia por ingresso, com confirmacao por e-mail. Bloqueada no dia do evento.

**Pontos Fortes:** QR que fica branco em screenshots comunicado como diferencial de marketing; Liberacao just-in-time reduz janela de ataque; Offline confirmado; PDF e Eventim.Pass como opcoes por tipo de evento.

**Pontos Fracos:** Sem integracao com Apple/Google Wallet no Brasil; Dependencia total do app Eventim Brasil; Usuarios relatam frustracao com ausencia de PDF para backup.

---
