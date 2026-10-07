import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


API_URL = "https://v3.football.api-sports.io"

API_KEY_ENV = "API_FOOTBALL_KEY"

TIMEZONE = "America/Sao_Paulo"

# Quantidade de jogos que o BET-AI vai analisar por ciclo
MAX_GAMES = 3

# Quantidade de jogos candidatos pesquisados
CANDIDATE_GAMES = 12

# Intervalo entre chamadas
REQUEST_INTERVAL = 8

# Timeout
REQUEST_TIMEOUT = 30

# Tentativas em caso de erro temporário
MAX_RETRIES = 2

# Proteção contra excesso de chamadas em uma execução
MAX_REQUESTS_PER_RUN = 12

# Probabilidade mínima para um sinal
MIN_PROBABILITY = 60.0

# Probabilidade considerada forte
HIGH_PROBABILITY = 75.0

# Edge mínimo quando houver odds
MIN_EDGE = 3.0

# Número máximo de seleções
MAX_SELECTIONS = 3


def get_api_key():
    key = os.getenv(API_KEY_ENV)

    if not key:
        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada no ambiente."
        )

    return key


def get_analysis_date():
    """
    Retorna a data atual no horário de São Paulo.

    Pode ser sobrescrita pelo GitHub Actions usando:
    ANALYSIS_DATE=2026-10-07
    """

    override = os.getenv("ANALYSIS_DATE", "").strip()

    if override:
        return override

    now = datetime.now(
        ZoneInfo(TIMEZONE)
    )

    return now.strftime("%Y-%m-%d")


def get_search_end_date():
    """
    Procura partidas de hoje até os próximos 3 dias.
    """

    today = datetime.now(
        ZoneInfo(TIMEZONE)
    ).date()

    end = today + timedelta(days=3)

    return end.strftime("%Y-%m-%d")
