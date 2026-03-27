# Play Insights — Database Cleanup Automático

## 🚀 Quick Start (5 minutos)

### 1️⃣ Ativar o Cleanup

Abra PowerShell como Administrador e execute:

```powershell
cd "C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports"
powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
```

Isso irá:
- Validar seu ambiente
- Criar tarefa agendada `PlayInsights-DatabaseCleanup`
- Agendar para **toda segunda-feira às 07:00**

### 2️⃣ Testar

```powershell
python scripts\cleanup_database.py
```

Você verá algo como:

```
2026-03-27 09:58:22 | INFO    | Play Insights - Database Cleanup
2026-03-27 09:58:22 | INFO    | ✓ vitals_daily: 390 registros removidos
2026-03-27 09:58:22 | INFO    | ✓ VACUUM: banco compactado com sucesso
2026-03-27 09:58:22 | INFO    | Limpeza concluída com sucesso!
```

### 3️⃣ Verificar o Log

```powershell
Get-Content -Tail 30 "$env:LOCALAPPDATA\play_insights\cleanup.log"
```

**Pronto!** A tarefa está ativa e rodará **toda segunda-feira às 07:00**.

---

## 📋 O Que Faz

O cleanup automático:

1. Remove dados antigos (> 90 dias) de 4 tabelas
2. Compacta o banco com `VACUUM`
3. Registra tudo em um log

| Tabela | Remove | Coluna |
|--------|--------|--------|
| reviews_raw | > 90 dias | ingest_date |
| error_issues | > 90 dias | ingest_date |
| vitals_daily | > 90 dias | date |
| stats_daily | > 90 dias | date |

**Benefício**: Reduz tamanho do banco em ~50-200 MB/semana

---

## 📁 Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `cleanup_database.py` | ⭐ Script principal (Python) |
| `cleanup_launcher.ps1` | ⭐ Wrapper (PowerShell) |
| `setup_cleanup_scheduler.ps1` | ⭐ Setup (criar tarefa) |
| `CLEANUP_README.md` | 📖 Manual completo |
| `INTEGRATION_GUIDE.md` | 🔗 Como se integra |

**⭐** = Essencial | **📖** = Referência

---

## 🔍 Monitorar

**Ver log semanal**:
```powershell
Get-Content "$env:LOCALAPPDATA\play_insights\cleanup.log"
```

**Ver status da tarefa**:
```powershell
Get-ScheduledTaskInfo -TaskName "PlayInsights-DatabaseCleanup"
```

**Ver tamanho do banco**:
```powershell
(Get-Item "$env:LOCALAPPDATA\play_insights\play_insights.duckdb").Length / 1MB
```

---

## ✅ Checklist

- [ ] Executou `setup_cleanup_scheduler.ps1` com sucesso
- [ ] Testou `python scripts\cleanup_database.py` e funcionou
- [ ] Verificou o log em `%LOCALAPPDATA%\play_insights\cleanup.log`
- [ ] Confirmou tarefa agendada (segunda-feira às 07:00)

---

## ❓ Dúvidas?

1. **"Preciso fazer algo?"** → Só executar o setup uma vez (acima)
2. **"Pode quebrar meu banco?"** → Não, usa `VACUUM` padrão do DuckDB
3. **"O que fazer se falhar?"** → Ver log em `%LOCALAPPDATA%\play_insights\cleanup.log`
4. **"Como desabilitar?"** → `Unregister-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup" -Confirm:$false`

Para mais detalhes, ver `CLEANUP_README.md`.

---

## 📊 Resultado Esperado

Após o setup:
- ✅ Tarefa agendada
- ✅ Executa toda segunda-feira às 07:00
- ✅ Remove dados > 90 dias
- ✅ Banco reduz de tamanho (~50-200 MB/semana)
- ✅ Zero impacto no relatório manual (roda às 08:00)

---

**Versão**: 1.0
**Data**: 27/03/2026
**Status**: Pronto para produção
