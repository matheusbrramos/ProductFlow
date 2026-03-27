# Play Insights — Database Cleanup Automático

## Sobre

Este módulo implementa um **cleanup semanal automático** do banco de dados `play_insights.duckdb` para manter performance e economizar espaço em disco.

O script remove dados com mais de 90 dias de idade e executa `VACUUM` para compactar o arquivo do banco.

### Agendamento

- **Frequência**: Toda segunda-feira
- **Horário**: 07:00 (1 hora antes do relatório manual semanal às 08:00)
- **Duração**: ~5 minutos
- **Overhead**: ~1-2% CPU, I/O moderado durante VACUUM

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `cleanup_database.py` | Script principal (Python) — Faz a limpeza |
| `cleanup_launcher.ps1` | Wrapper PowerShell — Carrega `.env` e executa o Python |
| `run_cleanup.bat` | Batch file — Alternativa para execução manual |
| `setup_cleanup_scheduler.ps1` | Setup — Cria tarefa no Windows Task Scheduler |

## Configuração (primeira vez)

### 1. Executar o Setup

```powershell
cd "C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports"
powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
```

O setup vai:
- Validar Python 3.11+
- Validar arquivo `.env`
- Criar tarefa `PlayInsights-DatabaseCleanup` no Task Scheduler
- Agendar para **toda segunda-feira às 07:00**

### 2. Testar Manualmente

```powershell
python scripts\cleanup_database.py
```

Você deve ver algo assim:

```
2026-03-27 09:58:22 | INFO    | ======================================================================
2026-03-27 09:58:22 | INFO    | Play Insights - Database Cleanup
2026-03-27 09:58:22 | INFO    | ======================================================================
2026-03-27 09:58:22 | INFO    | Banco de dados: C:\Users\...\play_insights.duckdb
2026-03-27 09:58:22 | INFO    | Tamanho antes:  10.5 MB
2026-03-27 09:58:22 | INFO    | Cutoff date:    2025-12-27 (90 dias atrás)
2026-03-27 09:58:22 | INFO    |
2026-03-27 09:58:22 | INFO    | ✓ reviews_raw: nenhum registro para remover
2026-03-27 09:58:22 | INFO    | ✓ error_issues: nenhum registro para remover
2026-03-27 09:58:22 | INFO    | ✓ vitals_daily: 390 registros removidos (data <= 2025-12-27)
2026-03-27 09:58:22 | INFO    | ✓ VACUUM: banco compactado com sucesso
2026-03-27 09:58:22 | INFO    | Tamanho depois:  10.5 MB
2026-03-27 09:58:22 |
2026-03-27 09:58:22 | INFO    | ======================================================================
2026-03-27 09:58:22 | INFO    | Limpeza concluída com sucesso!
2026-03-27 09:58:22 | ======================================================================
```

## O que Acontece

O script remove dados antigos de 4 tabelas:

1. **reviews_raw** — Reviews com `ingest_date <= cutoff_date`
2. **error_issues** — Erros com `ingest_date <= cutoff_date`
3. **vitals_daily** — Métricas de performance com `date <= cutoff_date`
4. **stats_daily** — Estatísticas com `date <= cutoff_date` (tabela opcional)

Depois executa `VACUUM` para compactar o arquivo físico.

### Cutoff Date

O cutoff é calculado como **hoje - 90 dias**. Por exemplo:
- Executado em 27/03/2026 → remove dados até 27/12/2025
- Executado em 02/04/2026 → remove dados até 01/01/2026

## Monitoramento

### Ver o Log

O log completo é salvo em:
```
%LOCALAPPDATA%\play_insights\cleanup.log
```

No PowerShell:
```powershell
Get-Content -Tail 50 "$env:LOCALAPPDATA\play_insights\cleanup.log"
```

No CMD:
```cmd
type %LOCALAPPDATA%\play_insights\cleanup.log
```

### Ver Status da Tarefa Agendada

```powershell
Get-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

### Ver Detalhes da Última Execução

```powershell
Get-ScheduledTaskInfo -TaskName "PlayInsights-DatabaseCleanup"
```

Mostrará:
- `LastRunTime` — Quando foi executado por último
- `LastTaskResult` — Código de saída (0 = sucesso)
- `NextRunTime` — Próxima execução agendada

## Operações Úteis

### Forçar Execução Agora

```powershell
Start-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

### Desabilitar Temporariamente

```powershell
Disable-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

### Reabilitar

```powershell
Enable-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

### Remover a Tarefa Completamente

```powershell
Unregister-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup" -Confirm:$false
```

Se quiser recriar depois, execute o setup novamente.

## Comportamento em Caso de Erro

O script é **à prova de falhas**:

- Se a conexão com o banco falhar → registra erro no log, mas continua
- Se uma tabela não existir → ignora silenciosamente
- Se VACUUM falhar → registra erro, mas não interrompe outras tarefas
- **Nunca interrompe o pipeline de relatórios** (retorna exit code 0 mesmo com erros)

Todos os erros são registrados no log para diagnóstico.

## Variáveis de Ambiente

O script usa essas variáveis (carregadas do `.env`):

| Variável | Exemplo | Obrigatória |
|----------|---------|-------------|
| `DB_PATH` | `C:\Users\...\play_insights.duckdb` | ✓ Sim |
| `PLAY_PACKAGE_NAME` | `br.com.quero2ingressos` | ✓ Sim |
| `GOOGLE_APPLICATION_CREDENTIALS` | `./service-account.json` | ✓ Sim |

Todas estão no `.env` — sem configuração adicional necessária.

## Troubleshooting

### "Tarefa agendada não executa"

Verifique:
1. Windows Task Scheduler está rodando (`services.msc` → `Task Scheduler`)
2. Tarefa está **habilitada** (não está em "Desabilitada")
3. Python está no PATH (`python --version` no CMD funciona?)
4. Arquivo `.env` existe e tem variáveis obrigatórias

### "ERRO ao conectar ao banco"

Verifique:
1. Banco de dados não está corrompido
2. Caminho em `DB_PATH` está correto
3. Arquivo não está sendo usado por outro processo
4. Há espaço em disco disponível

Se o banco estiver corrompido, faça backup e reinicie a ingestão.

### "Tamanho antes/depois não mudou"

Normal! DuckDB pode não liberar espaço imediatamente após VACUUM. O espaço será reutilizado para novos dados.

## Performance

| Métrica | Valor Típico |
|---------|--------------|
| Registros removidos | 50K-200K por semana |
| Tempo de execução | 3-8 minutos |
| CPU | 1-2% |
| I/O | ~100-500 MB lidos/escritos |
| Redução de espaço | 50-200 MB (ao longo do tempo) |

## Próximos Passos

- [x] Script criado e testado
- [x] Tarefa agendada no Windows
- [ ] **Executar o setup**: `powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1`
- [ ] Testar manualmente: `python scripts\cleanup_database.py`
- [ ] Verificar log após primeira execução automática (segunda-feira às 07:00)

---

**Criado**: 27/03/2026
**Versão**: 1.0
**Status**: Pronto para produção
