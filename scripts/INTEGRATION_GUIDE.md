# Guia de Integração — Cleanup Automático

Este documento descreve como o cleanup automático se integra com o resto do pipeline Play Insights.

## Timeline Semanal

Toda segunda-feira, a seguinte sequência acontece:

```
06:00 -------- (nada acontece)
|
07:00 -------- [CLEANUP] Remove dados > 90 dias, compacta banco
|              Executado: Windows Task Scheduler "PlayInsights-DatabaseCleanup"
|              Script: scripts/cleanup_launcher.ps1 → cleanup_database.py
|              Duração: ~5 minutos
|              Log: %LOCALAPPDATA%\play_insights\cleanup.log
|
08:00 -------- [RELATÓRIO MANUAL] Coleta e gera relatório semanal
|              Executado: Manualmente ou via Cron
|              Script: scripts/send_weekly_report.py
|              Duração: 5-10 minutos
|              Ação: Ingestão de reviews + análise + envio de e-mail
|
08:30 -------- (processamento concluído)
```

## Filosofia de Integração

### 1. **Não-Intrusivo**

- Cleanup **não interfere** com o pipeline manual
- Se o cleanup falhar, o relatório continua normalmente
- Se o relatório estiver rodando, cleanup aguarda (file lock automático do DuckDB)

### 2. **Fail-Safe**

- Cleanup **nunca retorna erro** (`exit 0` sempre)
- Todos os erros são registrados no log, mas não interrompem
- Banco de dados está protegido contra corrupção por locks automáticos

### 3. **Observabilidade**

- Cada execução é registrada com timestamp
- Log contém quantidade de registros removidos
- Log contém tamanho antes/depois (para trend analysis)

## Dependências

### O Cleanup Depende De:

- ✓ Python 3.11+
- ✓ Arquivo `.env` com `DB_PATH`, `PLAY_PACKAGE_NAME`, `GOOGLE_APPLICATION_CREDENTIALS`
- ✓ DuckDB (já instalado como dependência de `play_insights`)
- ✓ Windows Task Scheduler (ou equivalente no seu OS)

### O Que Depende Do Cleanup:

- ✓ `send_weekly_report.py` — Esperado que o banco esteja compactado antes de rodar
- ✓ `generate_baseline.py` — Performance melhorada se banco foi limpo recentemente
- ✓ Qualquer outro script que use o banco — Beneficia de menos dados antigos

## Arquivo de Configuração

O cleanup **não precisa de configuração adicional**. Tudo está em `.env`:

```env
# Obrigatório
DB_PATH=C:\Users\...\AppData\Local\play_insights\play_insights.duckdb
PLAY_PACKAGE_NAME=br.com.quero2ingressos
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\...\service-account.json

# Opcional (defaults)
DUCKDB_MEMORY_LIMIT=512MB
DUCKDB_THREADS=2
TIMEZONE=America/Sao_Paulo
```

## Monitoramento e Alertas

### O que Monitorar

1. **Log Semanal** — Verifique após segunda-feira às 07:00

   ```powershell
   Get-Content -Tail 50 "$env:LOCALAPPDATA\play_insights\cleanup.log"
   ```

2. **Status da Tarefa** — Verifique se executa corretamente

   ```powershell
   Get-ScheduledTaskInfo -TaskName "PlayInsights-DatabaseCleanup"
   ```

3. **Tamanho do Banco** — Monitore redução ao longo do tempo

   ```powershell
   (Get-Item "$env:LOCALAPPDATA\play_insights\play_insights.duckdb").Length / 1MB
   ```

### Red Flags

- ❌ Tarefa não executa por 2+ semanas
- ❌ Tamanho do banco cresce indefinidamente (nunca reduz)
- ❌ Erros nos logs (procure por `ERROR` ou `✗`)
- ❌ Tempo de execução muito aumentado (> 15 minutos)

## Troubleshooting Integrado

### Se o Cleanup Falhar, o Relatório Continua?

**Sim.** O cleanup e o relatório são processos separados. Falhas no cleanup são registradas no log, mas não afetam a execução do relatório.

### Se o Relatório Estiver Rodando, o Cleanup Espera?

**Sim.** DuckDB usa locks de arquivo automáticos. Se o arquivo está em uso, o cleanup aguarda (com timeout de 30s no PowerShell).

### E se Ambos Rodarem Simultaneamente?

Tecnicamente improvável (cleanup às 07:00, relatório às 08:00), mas se acontecer:
1. DuckDB mantém consistência com locks
2. Uma tarefa aguarda a outra
3. Ambas completam normalmente

### Como Recriar a Tarefa se Algo Der Errado?

```powershell
# 1. Remover tarefa existente
Unregister-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup" -Confirm:$false

# 2. Recriar
powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
```

## Métricas Esperadas

| Métrica | Valor | Frequência |
|---------|-------|-----------|
| Registros removidos | 50K-200K | Semanal |
| Tempo de execução | 3-8 min | Semanal |
| CPU | 1-2% | Durante execução |
| Redução de espaço | 50-200 MB | Semana a semana |
| Taxa de sucesso | 100% | Esperado |

## Integração com CI/CD (Futuro)

Se quisermos adicionar cleanup a um pipeline de CI/CD no futuro:

```python
# Exemplar para integração em pipeline
from pathlib import Path
import subprocess
import sys

script_path = Path(__file__).parent / "scripts" / "cleanup_launcher.ps1"

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
    capture_output=True,
    text=True,
)

print(result.stdout)
if result.returncode != 0:
    print("AVISO: Cleanup falhou", file=sys.stderr)
    # Não interromper — é não-crítico
```

## Versioning

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 27/03/2026 | Versão inicial |

## Próximos Passos Recomendados

- [ ] Executar `setup_cleanup_scheduler.ps1`
- [ ] Testar manualmente: `python scripts\cleanup_database.py`
- [ ] Monitorar primeira execução automática (segunda-feira às 07:00)
- [ ] Verificar tamanho do banco semanalmente
- [ ] Arquivar logs antigos mensalmente

---

**Documento**: Guia de Integração — Cleanup Automático
**Versão**: 1.0
**Data**: 27/03/2026
**Status**: Pronto para produção
