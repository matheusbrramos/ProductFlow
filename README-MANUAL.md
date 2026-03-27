# Play Insights — Execução Manual do Relatório Semanal

> **Status**: Automação desativada (27/03/2026)
>
> O relatório semanal agora é executado **manualmente**, sob demanda. A tarefa agendada `PlayInsights-WeeklyReport` foi removida do Windows Task Scheduler.

---

## Como Executar Manualmente

### Pré-requisitos

1. Python 3.11+ instalado
2. Variáveis de ambiente configuradas em `.env`
3. Credenciais Google Play Console (`service-account.json`)
4. Credenciais de e-mail (SMTP) configuradas

### Comando Básico

```bash
cd "C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports"
python scripts/send_weekly_report.py
```

### Opções

#### Modo Dry-Run (testa sem enviar e-mail)

```bash
python scripts/send_weekly_report.py --dry-run
```

Mostrará:
- Quem está recebendo o e-mail
- Assunto do e-mail
- Tamanho do relatório em HTML
- **Nenhum e-mail será enviado**

#### Pular Ingestão (usar dados já coletados)

```bash
python scripts/send_weekly_report.py --skip-ingest
```

Útil se você já rodou a ingestão e quer apenas regenerar o relatório.

#### Combinar Opções

```bash
python scripts/send_weekly_report.py --skip-ingest --dry-run
```

---

## O que Acontece ao Executar

### Pipeline Completo (padrão)

1. **Ingestão de Reviews** — Coleta reviews do Google Play Console (últimos 7 dias)
2. **Ingestão de Vitals** — Coleta crashes e ANRs (últimos 7 dias)
3. **Análise e Classificação** — Enriquece reviews com VOC e gera recomendações (30 dias)
4. **Geração de Relatório** — Cria arquivo Markdown com insights consolidados
5. **Envio de E-mail** — Envia para todos os destinatários em `REPORT_RECIPIENTS`

### Tempo Estimado

- Ingestão: 2-5 minutos
- Análise: 1-3 minutos
- Envio: < 1 minuto
- **Total: 5-10 minutos**

---

## Configuração de Variáveis de Ambiente

Todas as variáveis obrigatórias estão em `.env`:

### Obrigatórias

```env
SMTP_USER=matheus.ramos@q2ingressos.com.br          # E-mail remetente
SMTP_APP_PASSWORD=qeoj nrpx tglq nsiz               # Senha de app Gmail
REPORT_RECIPIENTS=...                                # Lista de destinatários
```

### Opcionais

```env
SMTP_HOST=smtp.gmail.com                            # Servidor SMTP (padrão: Gmail)
SMTP_PORT=587                                       # Porta SMTP (padrão: 587)
```

### Como Gerar Senha de App Gmail

1. Acesse: https://myaccount.google.com/
2. **Segurança** → **Senhas de app**
3. Selecione "Mail" e "Windows Computer"
4. Copie a senha gerada e cole em `SMTP_APP_PASSWORD`

---

## Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `scripts/send_weekly_report.py` | Script principal (executável) |
| `.env` | Configuração de variáveis de ambiente |
| `src/play_insights/` | Módulos do pipeline (ingest, analyze, report) |
| `docs/discovery/` | Relatórios semanais gerados (histórico) |

---

## Troubleshooting

### "ERRO: Variável de ambiente 'SMTP_USER' não configurada"

**Solução**: Verifique se `.env` existe no diretório raiz do projeto e contém a variável.

### "Error: [Errno 2] No such file or directory: 'service-account.json'"

**Solução**: Confirme que `service-account.json` está em:
```
C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports\
```

### E-mail não chega

**Verifique**:
1. `SMTP_USER` e `SMTP_APP_PASSWORD` estão corretos
2. A senha é uma **Senha de App** (não a senha normal da conta)
3. A conta tem **2FA habilitado** (obrigatório para senhas de app)
4. Execute com `--dry-run` para confirmar que o e-mail está sendo montado

### Ingestão está lenta

O DuckDB está rodando com limite de 2 threads e 512MB de RAM para economizar recursos.
Se quiser aumentar, edite `.env`:
```env
DUCKDB_THREADS=4          # Aumentar de 2 para 4
DUCKDB_MEMORY_LIMIT=1GB   # Aumentar de 512MB para 1GB
```

---

## Cleanup Automático do Banco de Dados

O banco de dados `play_insights.duckdb` cresce indefinidamente à medida que novos dados são ingeridos. Para manter performance e economizar espaço em disco, há um script automático que remove dados com mais de 90 dias toda **segunda-feira às 07:00** (1 hora antes do relatório manual).

### Configuração Automática

O cleanup já está agendado! Para confirmar ou reconfigurar:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
```

Isso criará uma tarefa Windows chamada `PlayInsights-DatabaseCleanup`.

### O que o Cleanup Faz

A cada execução:

1. **Remove reviews antigos** — `reviews_raw` com `ingest_date` > 90 dias
2. **Remove erros antigos** — `error_issues` com `ingest_date` > 90 dias
3. **Remove vitals antigos** — `vitals_daily` com `date` > 90 dias
4. **Remove stats antigos** — `stats_daily` com `date` > 90 dias
5. **Compacta o banco** — Executa `VACUUM` para liberar espaço em disco
6. **Registra ações** — Log completo em `%LOCALAPPDATA%\play_insights\cleanup.log`

### Execução Manual (teste)

Para testar o script manualmente:

```bash
python scripts/cleanup_database.py
```

### Verificar Log

Para ver o histórico de execuções:

```bash
cat %LOCALAPPDATA%\play_insights\cleanup.log
```

Ou no PowerShell:

```powershell
Get-Content -Tail 50 "$env:LOCALAPPDATA\play_insights\cleanup.log"
```

### Monitoramento da Tarefa

**Ver status da tarefa:**
```powershell
Get-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

**Ver informações detalhadas (última execução, próxima execução, etc):**
```powershell
Get-ScheduledTaskInfo -TaskName "PlayInsights-DatabaseCleanup"
```

**Forçar execução agora (para teste):**
```powershell
Start-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

### Impacto Esperado

| Métrica | Valor |
|---------|-------|
| Frequência | 1x semana (segunda às 07:00) |
| Duração | ~5 minutos |
| CPU | ~1-2% |
| I/O | Moderado durante VACUUM |
| Registros removidos | Típico: 50K-200K/semana |
| Redução de espaço | ~50-200 MB/semana |

### Remover o Cleanup (se necessário)

```powershell
Unregister-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup" -Confirm:$false
```

---

## Integração com Task Scheduler (se quiser reativar automação)

Para reagendar (se precisar no futuro):

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts/send_weekly_report.py" `
  -WorkingDirectory "C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:00AM"

Register-ScheduledTask -TaskName "PlayInsights-WeeklyReport" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Próximos Passos Recomendados

- [ ] Testar com `--dry-run` para confirmar que tudo está funcionando
- [ ] Rodar manualmente uma vez para validar o relatório
- [ ] Se necessário, configurar lembretes para executar todo **segunda-feira às 9h**
- [ ] Arquivar relatórios antigos em `docs/discovery/` periodicamente

---

**Última atualização**: 27/03/2026
**Responsável**: Matheus Ramos
**Status**: Automação desativada (relatório manual) + Cleanup automático (segunda às 07:00)

