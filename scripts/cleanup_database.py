"""
Play Insights - Database Cleanup Script

Remove dados com mais de 90 dias do banco de dados play_insights.duckdb
para manter performance e economizar espaço em disco.

Executa toda segunda-feira às 07:00 (antes do script manual semanal).

Funcionalidades:
  - Remove reviews_raw com ingest_date < 90 dias atrás
  - Remove error_issues com ingest_date < 90 dias atrás
  - Remove vitals_daily com date < 90 dias atrás
  - Remove stats_daily com date < 90 dias atrás
  - Executa VACUUM para compactar o banco
  - Registra ações em log com timestamps

Log salvo em:
  C:\\Users\\<user>\\AppData\\Local\\play_insights\\cleanup.log

Segurança:
  - Falha silenciosamente em caso de erro (não interrompe pipelines)
  - Registra todas as ações e erros no log
  - Valida conexão com banco antes de prosseguir

USO:
  python scripts/cleanup_database.py

USO COM AGENDADOR WINDOWS:
  powershell -ExecutionPolicy Bypass -File scripts\\setup_cleanup_scheduler.ps1
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import os

# Allow running from the project root without installing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from play_insights.config import Settings  # noqa: E402
    from play_insights.duckdb_repo import DuckDBRepository  # noqa: E402
except ImportError as e:
    print(f"ERRO: Não foi possível importar módulos Play Insights: {e}")
    print("Certifique-se de que está executando a partir do diretório do projeto.")
    sys.exit(1)


# ================================================================
# Configuração de Log
# ================================================================

def _setup_logging() -> logging.Logger:
    """Configura logger para arquivo e console com timestamps."""
    # Criar diretório de log se não existir
    log_dir = Path.home() / "AppData" / "Local" / "play_insights"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "cleanup.log"

    # Logger com arquivo e console
    logger = logging.getLogger("play_insights.cleanup")
    logger.setLevel(logging.DEBUG)

    # Handler para arquivo (DEBUG+)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Handler para console (INFO+)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formato com timestamp
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# ================================================================
# Funções de Cleanup
# ================================================================

def _get_cutoff_date(days_ago: int = 90) -> str:
    """Retorna a data de cutoff (90 dias atrás) no formato YYYY-MM-DD."""
    cutoff = datetime.now() - timedelta(days=days_ago)
    return cutoff.strftime("%Y-%m-%d")


def _get_db_file_size(db_path: str) -> tuple[float, str]:
    """
    Retorna tamanho do banco em bytes e formatado em MB.
    Retorna (0, "0 MB") se arquivo não existir.
    """
    try:
        if not os.path.exists(db_path):
            return 0, "0 MB"
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_bytes, f"{size_mb:.1f} MB"
    except Exception as e:
        return 0, f"ERRO: {e}"


def cleanup_reviews_raw(repo: DuckDBRepository, cutoff_date: str, logger: logging.Logger) -> int:
    """Remove reviews_raw com ingest_date > cutoff_date."""
    try:
        # Contar registros antes
        before = repo.query(
            f"SELECT COUNT(*) as cnt FROM reviews_raw WHERE ingest_date <= '{cutoff_date}'"
        )
        count_before = before[0]["cnt"] if before else 0

        # Deletar
        if count_before > 0:
            repo._conn.execute(
                f"DELETE FROM reviews_raw WHERE ingest_date <= '{cutoff_date}'"
            )
            logger.info(f"✓ reviews_raw: {count_before} registros removidos (data <= {cutoff_date})")
            return count_before
        else:
            logger.info(f"✓ reviews_raw: nenhum registro para remover")
            return 0

    except Exception as e:
        logger.error(f"✗ reviews_raw: ERRO ao remover — {e}")
        return 0


def cleanup_error_issues(repo: DuckDBRepository, cutoff_date: str, logger: logging.Logger) -> int:
    """Remove error_issues com ingest_date > cutoff_date."""
    try:
        # Contar registros antes
        before = repo.query(
            f"SELECT COUNT(*) as cnt FROM error_issues WHERE ingest_date <= '{cutoff_date}'"
        )
        count_before = before[0]["cnt"] if before else 0

        # Deletar
        if count_before > 0:
            repo._conn.execute(
                f"DELETE FROM error_issues WHERE ingest_date <= '{cutoff_date}'"
            )
            logger.info(f"✓ error_issues: {count_before} registros removidos (data <= {cutoff_date})")
            return count_before
        else:
            logger.info(f"✓ error_issues: nenhum registro para remover")
            return 0

    except Exception as e:
        logger.error(f"✗ error_issues: ERRO ao remover — {e}")
        return 0


def cleanup_vitals_daily(repo: DuckDBRepository, cutoff_date: str, logger: logging.Logger) -> int:
    """Remove vitals_daily com date > cutoff_date."""
    try:
        # Contar registros antes
        before = repo.query(
            f"SELECT COUNT(*) as cnt FROM vitals_daily WHERE date <= '{cutoff_date}'"
        )
        count_before = before[0]["cnt"] if before else 0

        # Deletar
        if count_before > 0:
            repo._conn.execute(
                f"DELETE FROM vitals_daily WHERE date <= '{cutoff_date}'"
            )
            logger.info(f"✓ vitals_daily: {count_before} registros removidos (data <= {cutoff_date})")
            return count_before
        else:
            logger.info(f"✓ vitals_daily: nenhum registro para remover")
            return 0

    except Exception as e:
        logger.error(f"✗ vitals_daily: ERRO ao remover — {e}")
        return 0


def cleanup_stats_daily(repo: DuckDBRepository, cutoff_date: str, logger: logging.Logger) -> int:
    """Remove stats_daily com date > cutoff_date (se a tabela existir)."""
    try:
        # Contar registros antes (tabela pode não existir)
        before = repo.query(
            f"SELECT COUNT(*) as cnt FROM stats_daily WHERE date <= '{cutoff_date}'"
        )
        count_before = before[0]["cnt"] if before else 0

        # Deletar
        if count_before > 0:
            repo._conn.execute(
                f"DELETE FROM stats_daily WHERE date <= '{cutoff_date}'"
            )
            logger.info(f"✓ stats_daily: {count_before} registros removidos (data <= {cutoff_date})")
            return count_before
        else:
            logger.info(f"✓ stats_daily: nenhum registro para remover")
            return 0

    except Exception as e:
        # Silencioso se tabela não existir (é opcional)
        if "does not exist" in str(e):
            logger.debug(f"✓ stats_daily: tabela não existe ou vazia, ignorando")
            return 0
        logger.error(f"✗ stats_daily: ERRO ao remover — {e}")
        return 0


def vacuum_database(repo: DuckDBRepository, logger: logging.Logger) -> bool:
    """Executa VACUUM para compactar o banco."""
    try:
        repo._conn.execute("VACUUM")
        logger.info("✓ VACUUM: banco compactado com sucesso")
        return True
    except Exception as e:
        logger.error(f"✗ VACUUM: ERRO ao compactar — {e}")
        return False


# ================================================================
# Main
# ================================================================

def main() -> int:
    """Executa limpeza do banco de dados."""
    logger = _setup_logging()

    logger.info("=" * 70)
    logger.info("Play Insights - Database Cleanup")
    logger.info("=" * 70)

    try:
        # Carregar configurações
        try:
            settings = Settings.from_env()
        except Exception as e:
            logger.error(f"ERRO ao carregar configurações: {e}")
            logger.error("Certifique-se de que as variáveis de ambiente estão definidas")
            return 1

        db_path = settings.db_path
        logger.info(f"Banco de dados: {db_path}")

        # Obter tamanho antes
        size_before_bytes, size_before_str = _get_db_file_size(db_path)
        logger.info(f"Tamanho antes:  {size_before_str}")

        # Conectar ao banco
        try:
            repo = DuckDBRepository(db_path=db_path)
            logger.debug("Conexão com banco estabelecida")
        except Exception as e:
            logger.error(f"ERRO ao conectar ao banco: {e}")
            return 1

        # Calcular data de cutoff
        cutoff_date = _get_cutoff_date(days_ago=90)
        logger.info(f"Cutoff date:    {cutoff_date} (90 dias atrás)")
        logger.info("")

        # Executar limpeza
        total_deleted = 0
        total_deleted += cleanup_reviews_raw(repo, cutoff_date, logger)
        total_deleted += cleanup_error_issues(repo, cutoff_date, logger)
        total_deleted += cleanup_vitals_daily(repo, cutoff_date, logger)
        total_deleted += cleanup_stats_daily(repo, cutoff_date, logger)

        logger.info("")
        logger.info(f"Total de registros removidos: {total_deleted}")

        # Compactar banco
        logger.info("")
        vacuum_database(repo, logger)

        # Obter tamanho depois
        size_after_bytes, size_after_str = _get_db_file_size(db_path)
        reduction_bytes = size_before_bytes - size_after_bytes
        reduction_percent = (reduction_bytes / size_before_bytes * 100) if size_before_bytes > 0 else 0

        logger.info(f"Tamanho depois:  {size_after_str}")
        if reduction_bytes > 0:
            logger.info(f"Redução:        {reduction_bytes / (1024 * 1024):.1f} MB ({reduction_percent:.1f}%)")
        else:
            logger.info(f"Redução:        0 MB (nenhuma redução)")

        logger.info("")
        logger.info("=" * 70)
        logger.info("Limpeza concluída com sucesso!")
        logger.info("=" * 70)

        return 0

    except Exception as e:
        # Falha silenciosa - registra mas não interrompe
        logger.error("")
        logger.error("=" * 70)
        logger.error(f"ERRO CRÍTICO: {e}")
        logger.error("=" * 70)
        logger.error("Script continuará em execução, mas limpeza pode ter falhado")
        logger.exception("Stacktrace completo:")
        return 0  # Não retorna erro para não interromper pipelines


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
