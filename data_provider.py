import os
import time
import requests

API_URL = "https://v3.football.api-sports.io"

# API-Football permite poucas requisições por minuto.
# 8 segundos ajuda a evitar estouro do limite.
REQUEST_INTERVAL = 8


def get_headers():
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada no GitHub."
        )

    return {
        "x-apisports-key": api_key
    }


def api_get(endpoint, params=None):
    time.sleep(REQUEST_INTERVAL)

    response = requests.get(
        f"{API_URL}/{endpoint}",
        headers=get_headers(),
        params=params or {},
        timeout=30
    )

    try:
        data = response.json()
    except Exception:
        raise RuntimeError(
            f"Resposta inválida da API. HTTP {response.status_code}"
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Limite de requisições da API-Football atingido."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Erro HTTP {response.status_code}: {data}"
        )

    if data.get("errors"):
        raise RuntimeError(
            f"Erro da API-Football: {data['errors']}"
        )

    return data.get("response", [])


# ============================================================
# JOGOS DO DIA
# ============================================================

def get_fixtures(date):
    return api_get(
        "fixtures",
        {
            "date": date
        }
    )


def normalize_fixture(fixture):
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    league = fixture.get("league", {})
    info = fixture.get("fixture", {})

    home = teams.get("home", {})
    away = teams.get("away", {})

    return {
        "fixture_id": info.get("id"),
        "date": info.get("date"),

        "home": home.get("name"),
        "away": away.get("name"),

        "home_id": home.get("id"),
        "away_id": away.get("id"),

        "home_goals": goals.get("home"),
        "away_goals": goals.get("away"),

        "league": league.get("name"),
        "league_id": league.get("id"),

        # IMPORTANTE:
        # essa temporada será usada no histórico
        "season": league.get("season")
    }


def get_real_games(date):
    fixtures = get_fixtures(date)

    games = []

    for fixture in fixtures:
        game = normalize_fixture(fixture)

        if game["home"] and game["away"]:
            games.append(game)

    return games


# ============================================================
# HISTÓRICO DA EQUIPE
# ============================================================

def get_team_recent_fixtures(team_id, season):
    if not season:
        raise RuntimeError(
            f"Temporada não encontrada para a equipe {team_id}."
        )

    return api_get(
        "fixtures",
        {
            "team": team_id,
            "season": season
        }
    )


def calculate_team_form(team_id, games_required=10, season=None):

    if not season:
        raise RuntimeError(
            f"Temporada não encontrada para a equipe {team_id}."
        )

    fixtures = get_team_recent_fixtures(
        team_id,
        season
    )

    # Ordena do jogo mais recente para o mais antigo
    fixtures.sort(
        key=lambda x: x.get("fixture", {}).get("date", ""),
        reverse=True
    )

    played = 0
    wins = 0
    draws = 0
    losses = 0

    goals_for = 0
    goals_against = 0

    for fixture in fixtures:

        if played >= games_required:
            break

        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})

        home = teams.get("home", {})
        away = teams.get("away", {})

        home_id = home.get("id")
        away_id = away.get("id")

        home_goals = goals.get("home")
        away_goals = goals.get("away")

        # Ignora partidas sem resultado
        if home_goals is None or away_goals is None:
            continue

        if team_id == home_id:

            team_goals = home_goals
            opponent_goals = away_goals

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

    # Caso não existam jogos válidos
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

    points = (
        wins * 3
        + draws
    )

    form = points / (played * 3)

    return {
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,

        "goals_for_avg": round(
            goals_for / played,
            2
        ),

        "goals_against_avg": round(
            goals_against / played,
            2
        ),

        "form": round(
            form,
            4
        )
    }
