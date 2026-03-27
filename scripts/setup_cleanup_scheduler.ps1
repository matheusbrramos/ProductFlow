# ============================================================
# Play Insights - Agendador de Cleanup do Banco de Dados
# Windows Task Scheduler - toda segunda às 07:00
#
# Remove dados com mais de 90 dias para manter performance
# Roda 1 hora ANTES do script manual semanal (08:00)
# ============================================================
#
# USO:
#   1. Abra o PowerShell como Administrador
#   2. Execute:
#      powershell -ExecutionPolicy Bypass -File scripts\setup_cleanup_scheduler.ps1
#
# Para remover a tarefa:
#   Unregister-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup" -Confirm:$false
#
# Para ver o status:
#   Get-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
#   Get-ScheduledTaskInfo -TaskName "PlayInsights-DatabaseCleanup"
#
# Para forcar execucao:
#   Start-ScheduledTask -TaskName "PlayInsights-DatabaseCleanup"
# ============================================================

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------
# Configuracoes
# ---------------------------------------------------------------
$TaskName        = "PlayInsights-DatabaseCleanup"
$ProjectDir      = $PSScriptRoot | Split-Path -Parent
$LauncherPath    = Join-Path $ProjectDir "scripts\cleanup_launcher.ps1"
$PythonExe       = (Get-Command python -ErrorAction SilentlyContinue).Source
$DayOfWeek       = "Monday"
$RunAt           = "07:00"

# ---------------------------------------------------------------
# Validacoes
# ---------------------------------------------------------------
Write-Host "Play Insights - Setup de Cleanup do Banco de Dados" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $PythonExe) {
    Write-Host "ERRO: Python nao encontrado no PATH" -ForegroundColor Red
    Write-Host "Instale Python 3.11+ e tente novamente." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python encontrado: $PythonExe" -ForegroundColor Green

if (-not (Test-Path $LauncherPath)) {
    Write-Host "ERRO: Script launcher nao encontrado: $LauncherPath" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Script launcher encontrado: $LauncherPath" -ForegroundColor Green

if (-not (Test-Path $ProjectDir)) {
    Write-Host "ERRO: Diretorio do projeto nao encontrado: $ProjectDir" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Diretorio do projeto: $ProjectDir" -ForegroundColor Green

Write-Host ""
Write-Host "Verificando variáveis de ambiente necessárias..." -ForegroundColor Yellow

# Validar arquivo .env
$EnvFile = Join-Path $ProjectDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "AVISO: Arquivo .env nao encontrado em: $EnvFile" -ForegroundColor Yellow
    Write-Host "       O script usará variáveis de ambiente do sistema." -ForegroundColor Yellow
} else {
    Write-Host "✓ Arquivo .env encontrado" -ForegroundColor Green
}

Write-Host ""

# ---------------------------------------------------------------
# Confirmacao
# ---------------------------------------------------------------
Write-Host "CONFIGURACAO A SER CRIADA:" -ForegroundColor Cyan
Write-Host "  Nome da Tarefa: $TaskName" -ForegroundColor White
Write-Host "  Agenda:         Todo $DayOfWeek às $RunAt" -ForegroundColor White
Write-Host "  Launcher:       $LauncherPath" -ForegroundColor White
Write-Host "  Diretorio:      $ProjectDir" -ForegroundColor White
Write-Host "  Timeout:        30 minutos" -ForegroundColor White
Write-Host ""

$Continue = Read-Host "Deseja continuar? (s/N)"
if ($Continue -ne "s" -and $Continue -ne "S") {
    Write-Host "Cancelado." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# ---------------------------------------------------------------
# Remover tarefa existente (se houver)
# ---------------------------------------------------------------
$Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "Removendo tarefa existente com mesmo nome..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null
    Start-Sleep -Milliseconds 500
}

# ---------------------------------------------------------------
# Criar a tarefa agendada
# ---------------------------------------------------------------
Write-Host "Criando tarefa agendada..." -ForegroundColor Yellow

try {
    # Acao: executar PowerShell launcher (que carrega .env e executa Python)
    $Action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File ""$LauncherPath""" `
        -WorkingDirectory $ProjectDir

    # Trigger: toda segunda às 07:00
    $Trigger = New-ScheduledTaskTrigger `
        -Weekly `
        -DaysOfWeek $DayOfWeek `
        -At $RunAt

    # Configuracoes da tarefa
    $TaskSettings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
        -RestartCount 2 `
        -RestartInterval (New-TimeSpan -Minutes 15) `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable

    # Principal: executar com usuario atual, nivel normal
    $Principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Limited

    # Registrar tarefa
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $TaskSettings `
        -Principal $Principal `
        -Description "Play Insights - limpeza semanal do banco de dados (90+ dias)" `
        | Out-Null

    Write-Host "✓ Tarefa criada com sucesso!" -ForegroundColor Green

} catch {
    Write-Host "ERRO ao criar tarefa: $_" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------
# Resumo e proximos passos
# ---------------------------------------------------------------
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "SUCESSO!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

Write-Host "A tarefa '$TaskName' foi criada e será executada:" -ForegroundColor Green
Write-Host "  → Toda segunda-feira às $RunAt" -ForegroundColor Green
Write-Host "  → Remove dados com mais de 90 dias" -ForegroundColor Green
Write-Host "  → Compacta o banco (VACUUM)" -ForegroundColor Green
Write-Host "  → Log registrado em AppData\Local\play_insights\cleanup.log" -ForegroundColor Green
Write-Host ""

Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "  1. Teste o script manualmente:" -ForegroundColor White
Write-Host "     powershell -NoProfile -ExecutionPolicy Bypass -File scripts\cleanup_launcher.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Ou teste o Python diretamente (com .env carregado):" -ForegroundColor White
Write-Host "     python scripts\cleanup_database.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Verifique o log:" -ForegroundColor White
Write-Host "     Get-Content -Tail 50 `$env:LOCALAPPDATA\play_insights\cleanup.log" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Para forcar execucao agora (teste):" -ForegroundColor White
Write-Host "     Start-ScheduledTask -TaskName ""$TaskName""" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Para ver status e ultima execucao:" -ForegroundColor White
Write-Host "     Get-ScheduledTaskInfo -TaskName ""$TaskName""" -ForegroundColor Gray
Write-Host ""
Write-Host "  6. Para remover a tarefa (se necessario):" -ForegroundColor White
Write-Host "     Unregister-ScheduledTask -TaskName ""$TaskName"" -Confirm:`$false" -ForegroundColor Gray
Write-Host ""

Write-Host "=" * 60 -ForegroundColor Green
