import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


API_URL = "https://v3.football.api-sports.io"

API_KEY_ENV = "API_FOOTBALL_KEY"

TIMEZONE = "America/Sao_Paulo"

MAX_GAMES = 3

CANDIDATE_GAMES = 12

REQUEST_INTERVAL = 8

REQUEST_TIMEOUT = 30

MAX_RETRIES = 2

MAX_REQUESTS_PER_RUN = 12

MIN_PROBABILITY = 60.0

HIGH_PROBABILITY = 75.0

MIN_EDGE = 3.0

MAX_SELECTIONS = 3


def get_api_key():

    key = os.getenv(API_KEY_ENV)

    if not key:

        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada no GitHub."
        )

    return key.strip()


def get_analysis_date():

    override = os.getenv(
        "ANALYSIS_DATE",
        ""
    ).strip()

    if override:

        return override

    now = datetime.now(
        ZoneInfo(TIMEZONE)
    )

    return now.strftime(
        "%Y-%m-%d"
    )


def get_search_dates(days=4):

    start = datetime.strptime(
        get_analysis_date(),
        "%Y-%m-%d"
    ).date()

    return [
        (
            start + timedelta(days=i)
        ).strftime("%Y-%m-%d")
        for i in range(days)
    ]
