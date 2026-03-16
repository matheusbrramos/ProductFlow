"""Crash pattern analysis — traduz dados técnicos de crash em narrativa acionável.

Gera duas versões de cada diagnóstico:
- Para stakeholders: linguagem leiga, analogias do dia a dia, impacto em negócio
- Para o time de desenvolvimento: causa provável, próximos passos técnicos concretos
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Thresholds para classificação de severidade
CRASH_RATE_CRITICAL = 0.15   # 15%+ — app-breaking, risco de demoção
CRASH_RATE_HIGH     = 0.05   # 5–15% — crítico para usuários
CRASH_RATE_MODERATE = 0.02   # 2–5%  — elevado, acima da política Google (1.09%)
CRASH_RATE_LOW      = 0.01   # <2%   — dentro ou próximo do aceitável

# Mapeamento Android API Level → nome da versão
ANDROID_API_NAMES: dict[str, str] = {
    "21": "Android 5.0 (Lollipop)",
    "22": "Android 5.1 (Lollipop)",
    "23": "Android 6.0 (Marshmallow)",
    "24": "Android 7.0 (Nougat)",
    "25": "Android 7.1 (Nougat)",
    "26": "Android 8.0 (Oreo)",
    "27": "Android 8.1 (Oreo)",
    "28": "Android 9.0 (Pie)",
    "29": "Android 10",
    "30": "Android 11",
    "31": "Android 12",
    "32": "Android 12L",
    "33": "Android 13",
    "34": "Android 14",
    "35": "Android 15",
    "36": "Android 16 (preview)",
}

# Padrões conhecidos de crashes Android com causa técnica provável
PATTERN_CAUSES: dict[str, str] = {
    "android_version": (
        "Incompatibilidade com versão recente do Android. "
        "APIs obsoletas, mudanças de ciclo de vida de Activity/Fragment, "
        "novas restrições de permissão ou comportamento alterado de intents."
    ),
    "regression": (
        "Regressão introduzida em um deploy recente. "
        "Alguma mudança de código ou dependência quebrou funcionalidade estável."
    ),
    "device_specific": (
        "Incompatibilidade com hardware ou camada de personalização do fabricante "
        "(Samsung OneUI, Motorola My UX, etc.). Pode ser related a GPU, "
        "renderização nativa, drivers, ou sensor específico do dispositivo."
    ),
    "widespread": (
        "Falha generalizada sem padrão claro de versão ou dispositivo. "
        "Causas prováveis: falha na inicialização do app (Application.onCreate), "
        "crash em componente core (Room database, DI framework, Firebase), "
        "ou condição de corrida em código assíncrono."
    ),
}

PATTERN_DEV_RECS: dict[str, list[str]] = {
    "android_version": [
        "Reproduzir em emulador Android 15 (API 35) — criar um emulador Pixel com API 35 no AVD Manager",
        "Verificar `targetSdkVersion` e `compileSdkVersion` no `build.gradle` — atualizar para 35 se necessário",
        "Revisar uso de APIs deprecated no Android 14/15: `onBackPressed()`, `startActivityForResult()`, intents com flags restritas",
        "Checar mudanças de ciclo de vida: Android 15 alterou comportamento de `Activity` em modo PiP e split-screen",
        "Verificar permissões: Android 14+ exige declaração explícita de `FOREGROUND_SERVICE_TYPE`",
        "Filtrar crashes no Play Console por Android API 35 e ver o stack trace completo com `Caused by:`",
        "Integrar Firebase Crashlytics se não ativo — captura stack traces completos em tempo real",
    ],
    "regression": [
        "Comparar o diff de código entre as versões afetadas (git diff vOld..vNew)",
        "Verificar se alguma biblioteca (dependency) foi atualizada nesse release",
        "Reproduzir em dispositivos da lista de hotspots (Samsung a25x, Motorola lamul)",
        "Avaliar rollback para versão anterior enquanto hotfix é preparado",
        "Prioridade: lançar versão corretiva em menos de 72h para limitar impacto",
        "Verificar o stack trace do crash no Play Console — o `Caused by:` vai indicar a linha exata",
    ],
    "device_specific": [
        "Reproduzir em Firebase Test Lab com os modelos afetados (Samsung a25x, Motorola lamul)",
        "Verificar se o crash ocorre com renderização por hardware (OpenGL/Vulkan) — testar com `--disable-gpu`",
        "Checar uso de código nativo (JNI/NDK) que pode ter comportamento diferente por chipset",
        "Verificar integração com sensores específicos (câmera, NFC, biometria) nesses dispositivos",
        "Considerar BrowserStack Device Cloud ou físico emprestado para reprodução",
        "Filtrar o crash no Play Console por modelo de dispositivo para ver o stack trace completo",
    ],
    "widespread": [
        "Verificar `Application.onCreate()` — qualquer exceção aqui derruba todos os usuários",
        "Checar inicialização de DI framework (Hilt, Koin, Dagger) — falha aqui = 100% de crash",
        "Revisar tratamento de erros em chamadas de rede — resposta inesperada pode causar crash em parse",
        "Checar se há race condition em código assíncrono (Coroutines, Flow) na inicialização",
        "Usar Android Studio → Logcat com filtro `crash` para capturar o stack trace em sessão local",
        "Verificar se Firebase Crashlytics ou similar está configurado — sem ele os stack traces ficam ocultos",
    ],
}


@dataclass
class CrashDiagnosis:
    """Diagnóstico completo de padrão de crash, com narrativas dual-audience."""
    severity_label: str          # ex.: "🔴 CRÍTICO"
    pattern_type: str            # "android_version" | "regression" | "device_specific" | "widespread"
    # Para stakeholders
    stakeholder_summary: str     # O que está acontecendo em linguagem leiga
    business_impact: str         # Impacto concreto no negócio
    hotspot_summary: str         # Onde está mais concentrado (leigo)
    # Para o time de dev
    technical_cause: str         # Causa técnica provável
    dev_recommendations: list[str] = field(default_factory=list)


def _severity_label(crash_avg: float) -> str:
    if crash_avg >= CRASH_RATE_CRITICAL:
        return "🔴 CRÍTICO"
    if crash_avg >= CRASH_RATE_HIGH:
        return "🟠 ALTO"
    if crash_avg >= CRASH_RATE_MODERATE:
        return "🟡 MODERADO"
    return "🟢 BAIXO"


def _detect_pattern(
    crash_avg: float,
    crash_by_version: list[dict[str, Any]],
    crash_by_device: list[dict[str, Any]],
) -> str:
    """Detecta o padrão dominante de crash a partir dos dados de vitals."""
    # 1. Regressão: versão atual muito pior que a anterior
    if len(crash_by_version) >= 2:
        sorted_v = sorted(crash_by_version, key=lambda x: x.get("last_seen") or "", reverse=True)
        curr = sorted_v[0].get("crash_avg_pct") or 0.0
        prev = sorted_v[1].get("crash_avg_pct") or 0.0
        if prev > 0 and curr > prev * 1.30:  # 30% pior
            return "regression"

    # 2. Android version: maioria dos hotspots em API 34+
    if crash_by_device:
        api_vals = []
        for r in crash_by_device:
            api = str(r.get("os_version") or "")
            if api.isdigit():
                api_vals.append(int(api))
        high_api_count = sum(1 for v in api_vals if v >= 34)
        if api_vals and high_api_count / len(api_vals) >= 0.5:
            return "android_version"

    # 3. Device-specific: dispositivo top é muito pior que a média
    if crash_by_device:
        top_crash = crash_by_device[0].get("crash_pct") or 0.0
        if crash_avg > 0 and top_crash > (crash_avg * 100) * 2.0:
            return "device_specific"

    return "widespread"


def _build_business_impact(crash_avg: float) -> str:
    """Frase de impacto no negócio, em linguagem concreta."""
    sessions_to_crash = int(round(1 / crash_avg)) if crash_avg > 0 else 0
    if crash_avg >= CRASH_RATE_CRITICAL:
        return (
            f"A cada **{sessions_to_crash} tentativas de abrir o app**, "
            f"**1 termina com o app fechando sozinho**. "
            f"Se o app tem 10.000 sessões diárias, aproximadamente "
            f"**{int(crash_avg * 10_000):,} usuários por dia** não conseguem usar o app. "
            "Cada crash = usuário que potencialmente abandona a compra, deixa avaliação negativa "
            "ou desinstala o app."
        )
    if crash_avg >= CRASH_RATE_HIGH:
        return (
            f"**1 em cada {sessions_to_crash} sessões** termina em crash — "
            "impacto significativo em conversão e retenção. "
            "Usuários afetados tendem a não tentar novamente."
        )
    return (
        f"Crash rate de **{crash_avg:.1%}** acima da meta recomendada pelo Google (1.09%). "
        "Ainda não crítico, mas se não tratado tende a piorar com cada novo release."
    )


def _build_stakeholder_summary(
    pattern: str,
    crash_avg: float,
    crash_by_device: list[dict[str, Any]],
    crash_by_version: list[dict[str, Any]],
) -> str:
    crash_pct = crash_avg * 100

    if pattern == "android_version":
        api_vals = sorted(set(
            str(r.get("os_version") or "")
            for r in crash_by_device
            if str(r.get("os_version") or "").isdigit() and int(str(r.get("os_version") or "0")) >= 34
        ))
        api_names = [ANDROID_API_NAMES.get(v, f"Android API {v}") for v in api_vals[:3]]
        api_str = " e ".join(api_names) if api_names else "versões recentes do Android (14/15)"
        return (
            f"O app está travando principalmente em usuários com **{api_str}**. "
            "Isso indica que uma atualização recente do sistema operacional mudou alguma regra "
            "que o app ainda não está preparado para seguir. "
            "É como se o governo publicasse uma nova lei de trânsito e o GPS do carro "
            "ainda não soubesse das mudanças — o app não sabe como se comportar nesse novo ambiente."
        )

    if pattern == "regression":
        sorted_v = sorted(crash_by_version, key=lambda x: x.get("last_seen") or "", reverse=True)
        curr_ver = sorted_v[0].get("app_version") or "atual" if sorted_v else "atual"
        prev_ver = sorted_v[1].get("app_version") or "anterior" if len(sorted_v) > 1 else "anterior"
        curr_crash = sorted_v[0].get("crash_avg_pct") or 0.0 if sorted_v else 0.0
        prev_crash = sorted_v[1].get("crash_avg_pct") or 0.0 if len(sorted_v) > 1 else 0.0
        return (
            f"O número de crashes **aumentou significativamente após o último deploy** "
            f"(versão `{curr_ver}`: {curr_crash:.1f}% vs. versão `{prev_ver}`: {prev_crash:.1f}%). "
            "Isso indica que uma mudança feita nessa atualização introduziu um problema. "
            "É como um defeito de fábrica: um lote saiu com problema. "
            "Identificar e reverter a mudança deve resolver o crash."
        )

    if pattern == "device_specific":
        top = crash_by_device[:3]
        names = [r.get("device_model") or "?" for r in top]
        return (
            f"Os crashes estão concentrados em **dispositivos específicos**: {', '.join(names)}. "
            "A maioria dos usuários em outros aparelhos não é afetada. "
            "Pense como um produto que funciona bem na maioria das tomadas, "
            "mas quebra num modelo específico — é incompatibilidade de hardware."
        )

    # widespread
    return (
        f"O app está travando com frequência em **{crash_pct:.0f}% das sessões** — "
        f"**{int(crash_pct / 1.09):.0f}x acima do limite recomendado** pelo Google Play. "
        "Não é um problema isolado: afeta usuários de forma generalizada, "
        "independente do dispositivo ou versão do Android. "
        "É como um vazamento que atinge vários andares ao mesmo tempo."
    )


def _build_hotspot_summary(
    crash_by_device: list[dict[str, Any]],
    crash_by_version: list[dict[str, Any]],
) -> str:
    parts: list[str] = []

    if crash_by_device:
        worst = crash_by_device[0]
        device = worst.get("device_model") or "?"
        api = str(worst.get("os_version") or "")
        android_name = ANDROID_API_NAMES.get(api, f"Android API {api}" if api else "versão desconhecida")
        pct = worst.get("crash_pct") or 0.0
        parts.append(
            f"O modelo mais afetado é **{device}** ({android_name}) com "
            f"**{pct:.0f}%** de crash — ou seja, {int(pct)} em cada 100 sessões nesse aparelho travam."
        )

    if crash_by_version:
        sorted_v = sorted(crash_by_version, key=lambda x: x.get("last_seen") or "", reverse=True)
        curr = sorted_v[0]
        ver = curr.get("app_version") or "?"
        pct = curr.get("crash_avg_pct") or 0.0
        parts.append(f"A versão ativa **{ver}** tem crash rate médio de **{pct:.1f}%**.")

    return "  \n".join(parts)


def analyze_crash_patterns(
    crash_avg: float,
    crash_by_device: list[dict[str, Any]],
    crash_by_version: list[dict[str, Any]],
) -> CrashDiagnosis:
    """
    Analisa padrões de crash a partir dos dados de vitals e retorna um diagnóstico
    com narrativas para stakeholders e para o time de desenvolvimento.
    """
    if crash_avg <= 0:
        return CrashDiagnosis(
            severity_label="🟢 BAIXO",
            pattern_type="widespread",
            stakeholder_summary="Nenhum dado de crash rate disponível para análise.",
            business_impact="Sem dados suficientes para estimar impacto.",
            hotspot_summary="",
            technical_cause="Sem dados.",
            dev_recommendations=[],
        )

    pattern = _detect_pattern(crash_avg, crash_by_version, crash_by_device)

    return CrashDiagnosis(
        severity_label=_severity_label(crash_avg),
        pattern_type=pattern,
        stakeholder_summary=_build_stakeholder_summary(pattern, crash_avg, crash_by_device, crash_by_version),
        business_impact=_build_business_impact(crash_avg),
        hotspot_summary=_build_hotspot_summary(crash_by_device, crash_by_version),
        technical_cause=PATTERN_CAUSES[pattern],
        dev_recommendations=PATTERN_DEV_RECS[pattern],
    )
