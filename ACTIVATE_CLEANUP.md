# Ativar Cleanup Automático — Instruções Rápidas

## 3 Passos para Ativar

### Passo 1: Abrir PowerShell como Administrador

1. Pressione `Win + X`
2. Selecione "Windows PowerShell (Admin)" ou "Terminal (Admin)"
3. Se pedir confirmação, clique "Sim"

### Passo 2: Navegar até o Projeto

Cole e execute no PowerShell:

```powershell
cd "C:\Users\matheus.santos_q2ing\Documents\Q2\App Google Reports"
```

### Passo 3: Executar o Setup

Cole e execute:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
```

A tela mostrará as configurações e pedirá confirmação. Digite `s` e pressione Enter.

---

## Pronto!

Após completar os 3 passos:

✅ **Tarefa agendada**: `PlayInsights-DatabaseCleanup`
✅ **Quando executa**: Toda segunda-feira às 07:00
✅ **Próxima execução**: Próxima segunda-feira às 07:00

---

## Testar Agora (Opcional)

Para testar o script **agora** (sem aguardar segunda-feira):

```powershell
python scripts\cleanup_database.py
```

Você verá logs detalhados. Se tudo correr bem, mostrará:
```
✓ vitals_daily: XXX registros removidos
✓ VACUUM: banco compactado com sucesso
Limpeza concluída com sucesso!
```

---

## Verificar Status

Para confirmar que a tarefa está agendada:

```powershell
Get-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
```

Se retornar informações da tarefa, está correto.

---

## Se Algo Deu Errado

Leia: `scripts/CLEANUP_README.md` seção "Troubleshooting"

Ou procure ajuda em: `scripts/00_START_HERE.md`

---

**Fim das instruções!** O cleanup agora roda automaticamente toda segunda-feira às 07:00.
