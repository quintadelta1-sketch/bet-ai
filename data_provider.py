import json
import os
import time
import requests
from datetime import datetime, timedelta


API_URL = "https://v3.football.api-sports.io"

CACHE_FILE = ".bet_ai_cache.json"

REQUEST_INTERVAL = 8

_last_request_time = 0


# ==========================================================
# CACHE
# ==========================================================

def load_cache():

    if not os.path.exists(CACHE_FILE):
        return {}

    try:

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_cache(cache):

    try:

        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as error:

        print(
            f"Aviso: não foi possível salvar cache: {error}"
        )


# ==========================================================
# AUTENTICAÇÃO
# ==========================================================

def get_headers():

    api_key = os.getenv(
        "API_FOOTBALL_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada no GitHub."
        )

    return {
        "x-apisports-key": api_key
    }


# ==========================================================
# CONTROLE DE REQUISIÇÕES
# ==========================================================

def wait_before_request():

    global _last_request_time

    now = time.time()

    elapsed = (
        now - _last_request_time
    )

    if elapsed < REQUEST_INTERVAL:

        wait_time = (
            REQUEST_INTERVAL
            - elapsed
        )

        print(
            f"Aguardando {round(wait_time, 1)}s..."
        )

        time.sleep(
            wait_time
        )

    _last_request_time = time.time()


# ==========================================================
# CONSULTA API
# ==========================================================

def api_get(
    endpoint,
    params=None
):

    wait_before_request()

    response = requests.get(
        f"{API_URL}/{endpoint}",
        headers=get_headers(),
        params=params or {},
        timeout=30
    )

    # ------------------------------------------------------
    # RATE LIMIT
    # ------------------------------------------------------

    if response.status_code == 429:

        raise RuntimeError(
            "RATE_LIMIT: a API-Football informou "
            "que o limite de 10 requisições por minuto "
            "foi atingido."
        )

    # ------------------------------------------------------
    # OUTROS ERROS
    # ------------------------------------------------------

    if response.status_code != 200:

        raise RuntimeError(
            f"API retornou HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "Resposta inválida da API-Football."
        )

    # ------------------------------------------------------
    # ERROS INTERNOS DA API
    # ------------------------------------------------------

    errors = data.get(
        "errors"
    )

    if errors:

        error_text = str(
            errors
        )

        if (
            "rateLimit" in error_text
            or "Too many requests" in error_text
        ):

            raise RuntimeError(
                "RATE_LIMIT: "
                "limite de 10 requisições por minuto."
            )

        raise RuntimeError(
            f"Erro da API-Football: "
            f"{errors}"
        )

    return data.get(
        "response",
        []
    )


# ==========================================================
# JOGOS DO DIA
# ==========================================================

def get_fixtures(date):

    return api_get(
        "fixtures",
        {
            "date": date
        }
    )


# ==========================================================
# NORMALIZAR JOGO
# ==========================================================

def normalize_fixture(
    fixture
):

    teams = fixture.get(
        "teams",
        {}
    )

    goals = fixture.get(
        "goals",
        {}
    )

    league = fixture.get(
        "league",
        {}
    )

    fixture_info = fixture.get(
        "fixture",
        {}
    )

    home = teams.get(
        "home",
        {}
    )

    away = teams.get(
        "away",
        {}
    )

    return {

        "fixture_id":
            fixture_info.get("id"),

        "date":
            fixture_info.get("date"),

        "home":
            home.get("name"),

        "away":
            away.get("name"),

        "home_id":
            home.get("id"),

        "away_id":
            away.get("id"),

        "home_goals":
            goals.get("home"),

        "away_goals":
            goals.get("away"),

        "league":
            league.get("name"),

        "league_id":
            league.get("id"),

        "season":
            league.get("season")
    }


# ==========================================================
# JOGOS REAIS
# ==========================================================

def get_real_games(
    date
):

    fixtures = get_fixtures(
        date
    )

    games = []

    for fixture in fixtures:

        game = normalize_fixture(
            fixture
        )

        if (
            game["home"]
            and game["away"]
            and game["home_id"]
            and game["away_id"]
        ):

            games.append(
                game
            )

    return games


# ==========================================================
# HISTÓRICO DA EQUIPE
# ==========================================================

def get_team_recent_fixtures(
    team_id,
    last=10
):

    if not team_id:

        raise RuntimeError(
            "ID da equipe não informado."
        )

    cache = load_cache()

    cache_key = (
        f"team_{team_id}_{last}"
    )

    # ------------------------------------------------------
    # VERIFICAR CACHE
    # ------------------------------------------------------

    if cache_key in cache:

        cached = cache[
            cache_key
        ]

        cached_time = cached.get(
            "timestamp",
            0
        )

        age = (
            time.time()
            - cached_time
        )

        # Cache válido por 30 minutos
        if age < 1800:

            print(
                f"Histórico da equipe "
                f"{team_id} "
                "carregado do cache."
            )

            return cached.get(
                "fixtures",
                []
            )

    # ------------------------------------------------------
    # CONSULTA ÚNICA
    # ------------------------------------------------------

    print(
        f"Consultando histórico "
        f"da equipe {team_id}..."
    )

    try:

        fixtures = api_get(
            "fixtures",
            {
                "team": team_id,
                "last": last
            }
        )

    except Exception as error:

        # NÃO FAZER SEGUNDA TENTATIVA
        # SE FOR RATE LIMIT

        if "RATE_LIMIT" in str(error):

            raise RuntimeError(
                "RATE_LIMIT: histórico da equipe "
                f"{team_id} não pôde ser consultado "
                "porque a API atingiu o limite."
            )

        raise

    # ------------------------------------------------------
    # SALVAR CACHE
    # ------------------------------------------------------

    cache[cache_key] = {

        "timestamp":
            time.time(),

        "fixtures":
            fixtures

    }

    save_cache(
        cache
    )

    return fixtures


# ==========================================================
# FORMA DA EQUIPE
# ==========================================================

def calculate_team_form(
    team_id,
    last=10
):

    fixtures = get_team_recent_fixtures(
        team_id,
        last
    )

    played = 0

    wins = 0

    draws = 0

    losses = 0

    goals_for = 0

    goals_against = 0

    for fixture in fixtures:

        teams = fixture.get(
            "teams",
            {}
        )

        goals = fixture.get(
            "goals",
            {}
        )

        home = teams.get(
            "home",
            {}
        )

        away = teams.get(
            "away",
            {}
        )

        home_id = home.get(
            "id"
        )

        away_id = away.get(
            "id"
        )

        home_goals = goals.get(
            "home"
        )

        away_goals = goals.get(
            "away"
        )

        # Ignorar partidas sem resultado

        if (
            home_goals is None
            or away_goals is None
        ):

            continue

        # --------------------------------------------------
        # EQUIPE CASA
        # --------------------------------------------------

        if team_id == home_id:

            team_goals = home_goals

            opponent_goals = away_goals

        # --------------------------------------------------
        # EQUIPE FORA
        # --------------------------------------------------

        elif team_id == away_id:

            team_goals = away_goals

            opponent_goals = home_goals

        else:

            continue

        played += 1

        goals_for += team_goals

        goals_against += opponent_goals

        if team_goals > opponent_goals:

            wins += 1

        elif team_goals == opponent_goals:

            draws += 1

        else:

            losses += 1

    # ------------------------------------------------------
    # SEM HISTÓRICO
    # ------------------------------------------------------

    if played == 0:

        return {

            "played": 0,

            "wins": 0,

            "draws": 0,

            "losses": 0,

            "goals_for_avg": 0,

            "goals_against_avg": 0,

            "form": 0.5
        }

    # ------------------------------------------------------
    # FORMA
    # ------------------------------------------------------

    points = (
        wins * 3
        + draws
    )

    form = (
        points
        / (played * 3)
    )

    return {

        "played":
            played,

        "wins":
            wins,

        "draws":
            draws,

        "losses":
            losses,

        "goals_for_avg":
            round(
                goals_for / played,
                2
            ),

        "goals_against_avg":
            round(
                goals_against / played,
                2
            ),

        "form":
            round(
                form,
                4
            )
    }


# ==========================================================
# TESTE
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "BET-AI - DATA PROVIDER"
    )

    print("=" * 60)

    today = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )

    print(
        f"Data: {today}"
    )

    print()

    try:

        games = get_real_games(
            today
        )

        print(
            f"Jogos encontrados: "
            f"{len(games)}"
        )

        for game in games[:5]:

            print(
                f"- {game['home']} "
                f"x "
                f"{game['away']}"
            )

        print()

        print(
            "DATA PROVIDER funcionando."
        )

    except Exception as error:

        print(
            f"ERRO: {error}"
        )
