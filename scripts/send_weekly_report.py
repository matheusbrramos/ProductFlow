"""
Envio automático do relatório semanal Play Insights por e-mail.

Executa o pipeline completo (ingest → analyze → report) e envia o
relatório semanal formatado em HTML para a lista de destinatários.

Uso manual:
    python scripts/send_weekly_report.py

Uso com --dry-run (não envia, apenas mostra o que seria enviado):
    python scripts/send_weekly_report.py --dry-run

Variáveis de ambiente obrigatórias (em .env):
    SMTP_USER              E-mail de origem (ex: matheus.ramos@q2ingressos.com.br)
    SMTP_APP_PASSWORD      Senha de app Gmail (não a senha normal da conta)
    REPORT_RECIPIENTS      Lista de destinatários separada por vírgula

Variáveis opcionais:
    SMTP_HOST              Padrão: smtp.gmail.com
    SMTP_PORT              Padrão: 587
    PLAY_PACKAGE_NAME      br.com.quero2ingressos
    DB_PATH                play_insights.duckdb
    GOOGLE_APPLICATION_CREDENTIALS  Caminho para service-account.json
"""
from __future__ import annotations

import argparse
import os
import smtplib
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Allow running from the project root without installing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from play_insights.config import Settings  # noqa: E402
from play_insights.duckdb_repo import DuckDBRepository  # noqa: E402
from play_insights.pipeline import analyze, ingest_errors, ingest_reviews, ingest_vitals  # noqa: E402
from play_insights.report_weekly import generate_weekly_report  # noqa: E402


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _load_dotenv() -> None:
    """Carrega .env do diretório do projeto (se existir)."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"ERRO: Variável de ambiente '{name}' não configurada.")
        print("      Adicione ao arquivo .env e tente novamente.")
        sys.exit(1)
    return val


# ---------------------------------------------------------------------------
# Markdown → HTML (sem dependências extras)
# ---------------------------------------------------------------------------

def _md_to_html(md: str) -> str:
    """Converte Markdown para HTML simples, suficiente para e-mail."""
    try:
        import markdown  # type: ignore
        body = markdown.markdown(md, extensions=["tables", "fenced_code"])
    except ImportError:
        # Fallback: conversão mínima sem biblioteca
        import re
        body = md
        # Headers
        body = re.sub(r"^### (.+)$", r"<h3>\1</h3>", body, flags=re.MULTILINE)
        body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", body, flags=re.MULTILINE)
        body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", body, flags=re.MULTILINE)
        # Bold / italic
        body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
        body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
        # Blockquotes
        body = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", body, flags=re.MULTILINE)
        # Horizontal rules
        body = re.sub(r"^---$", r"<hr>", body, flags=re.MULTILINE)
        # Line breaks
        body = body.replace("\n\n", "</p><p>")
        body = f"<p>{body}</p>"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 15px;
      line-height: 1.6;
      color: #1a1a1a;
      max-width: 860px;
      margin: 0 auto;
      padding: 24px;
      background: #f8f9fa;
    }}
    .container {{
      background: #ffffff;
      border-radius: 8px;
      padding: 32px 40px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
    h1 {{ color: #111; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
    h2 {{ color: #222; border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; margin-top: 32px; }}
    h3 {{ color: #333; margin-top: 20px; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0;
      font-size: 14px;
    }}
    th {{
      background: #f0f4f8;
      padding: 8px 12px;
      text-align: left;
      border: 1px solid #d0d7de;
    }}
    td {{
      padding: 7px 12px;
      border: 1px solid #d0d7de;
    }}
    tr:nth-child(even) td {{ background: #f9f9f9; }}
    blockquote {{
      border-left: 4px solid #0066cc;
      margin: 12px 0;
      padding: 8px 16px;
      background: #f0f7ff;
      border-radius: 0 4px 4px 0;
      color: #333;
    }}
    code {{
      background: #f0f0f0;
      padding: 2px 5px;
      border-radius: 3px;
      font-size: 13px;
      font-family: 'Courier New', monospace;
    }}
    hr {{ border: none; border-top: 1px solid #e8e8e8; margin: 24px 0; }}
    .footer {{
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid #e0e0e0;
      font-size: 12px;
      color: #888;
    }}
  </style>
</head>
<body>
  <div class="container">
    {body}
    <div class="footer">
      Relatório gerado automaticamente pelo Play Insights Pipeline ·
      <a href="https://play.google.com/console">Play Console</a>
    </div>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(settings: Settings) -> tuple[Path, int]:
    """Executa ingest + analyze + report semanal. Retorna (path_md, reviews_count)."""
    print("  [1/4] Ingestão de reviews...")
    r = ingest_reviews(settings=settings)
    reviews_count = r.get("fetched", 0)
    print(f"        {reviews_count} reviews coletados")

    print("  [2/4] Ingestão de vitals (7 dias)...")
    r = ingest_vitals(settings=settings, days=7)
    print(f"        {r.get('crash_count', 0)} crash + {r.get('anr_count', 0)} ANR segmentos")

    print("  [3/4] Análise e classificação VOC (30 dias)...")
    r = analyze(settings=settings, window_days=30)
    print(f"        {r.get('enriched_written', 0)} reviews enriquecidos, "
          f"{r.get('recommendations_written', 0)} recomendações")

    print("  [4/4] Gerando relatório semanal...")
    repo = DuckDBRepository(db_path=settings.db_path)
    path = generate_weekly_report(repo=repo, window=30)
    print(f"        Relatório: {path}")

    return path, reviews_count


# ---------------------------------------------------------------------------
# E-mail
# ---------------------------------------------------------------------------

def send_email(
    report_path: Path,
    smtp_user: str,
    smtp_password: str,
    recipients: list[str],
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    dry_run: bool = False,
) -> None:
    today = date.today()
    subject = (
        f"Q2 Ingressos — Relatório Semanal Play Store · "
        f"{today.strftime('%d/%m/%Y')}"
    )

    md_content = report_path.read_text(encoding="utf-8")
    html_body = _md_to_html(md_content)

    # Plain text fallback (first 3000 chars)
    plain_text = (
        f"Relatório Semanal Play Store — {today.isoformat()}\n\n"
        f"Arquivo completo: {report_path}\n\n"
        + md_content[:3000]
        + "\n\n[... conteúdo completo no arquivo em anexo]"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if dry_run:
        print("\n[DRY-RUN] E-mail que seria enviado:")
        print(f"  De:       {smtp_user}")
        print(f"  Para:     {', '.join(recipients)}")
        print(f"  Assunto:  {subject}")
        print(f"  Tamanho:  {len(html_body):,} chars HTML")
        print("  [Nenhum e-mail foi enviado]")
        return

    print(f"\nEnviando e-mail para {len(recipients)} destinatário(s)...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_bytes())

    print(f"E-mail enviado com sucesso para: {', '.join(recipients)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Enviar relatório semanal Play Insights por e-mail")
    parser.add_argument("--dry-run", action="store_true", help="Gera o relatório mas não envia o e-mail")
    parser.add_argument("--skip-ingest", action="store_true", help="Pula ingest/analyze, usa dados já existentes")
    args = parser.parse_args()

    _load_dotenv()

    # Validar configuração de e-mail
    smtp_user       = _require_env("SMTP_USER")
    smtp_password   = _require_env("SMTP_APP_PASSWORD")
    recipients_raw  = _require_env("REPORT_RECIPIENTS")
    recipients      = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    smtp_host       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port       = int(os.environ.get("SMTP_PORT", "587"))

    print(f"=== Play Insights — Envio Semanal ({date.today().isoformat()}) ===\n")
    print(f"Destinatários: {', '.join(recipients)}")
    print()

    # Pipeline
    settings = Settings.from_env()

    if args.skip_ingest:
        print("Pulando ingest (--skip-ingest). Usando dados existentes...")
        repo = DuckDBRepository(db_path=settings.db_path)
        report_path = generate_weekly_report(repo=repo, window=30)
    else:
        report_path, _ = run_pipeline(settings)

    # Envio
    send_email(
        report_path=report_path,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        recipients=recipients,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        dry_run=args.dry_run,
    )

    print("\nConcluído.")


if __name__ == "__main__":
    main()
