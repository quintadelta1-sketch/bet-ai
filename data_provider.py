import os
import requests
from datetime import datetime, timedelta

API_URL = "https://v3.football.api-sports.io"


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
    url = f"{API_URL}/{endpoint}"

    response = requests.get(
        url,
        headers=get_headers(),
        params=params or {},
        timeout=30
    )

    # Mostra erro HTTP de forma clara
    if response.status_code != 200:
        raise RuntimeError(
            f"API retornou HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    try:
        data = response.json()
    except Exception:
        raise RuntimeError(
            f"Resposta inválida da API: {response.text[:500]}"
        )

    # Erros informados pela própria API
    if data.get("errors"):
        raise RuntimeError(
            f"Erro da API-Football: {data['errors']}"
        )

    return data.get("response", [])


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


def normalize_fixture(fixture):
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    league = fixture.get("league", {})
    fixture_info = fixture.get("fixture", {})

    home = teams.get("home", {})
    away = teams.get("away", {})

    return {
        "fixture_id": fixture_info.get("id"),
        "date": fixture_info.get("date"),

        "home": home.get("name"),
        "away": away.get("name"),

        "home_id": home.get("id"),
        "away_id": away.get("id"),

        "home_goals": goals.get("home"),
        "away_goals": goals.get("away"),

        "league": league.get("name"),
        "league_id": league.get("id"),
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


# ==========================================================
# HISTÓRICO DA EQUIPE
# ==========================================================

def get_team_recent_fixtures(team_id, last=10):

    if not team_id:
        raise RuntimeError(
            "ID da equipe não informado."
        )

    # Primeiro tenta o método last
    try:

        fixtures = api_get(
            "fixtures",
            {
                "team": team_id,
                "last": last
            }
        )

        if fixtures:
            return fixtures

    except Exception as error:

        print(
            f"Aviso: consulta last={last} falhou para "
            f"equipe {team_id}: {error}"
        )

    # ======================================================
    # SEGUNDA TENTATIVA
    # Busca por intervalo de datas
    # ======================================================

    today = datetime.utcnow().date()

    date_from = today - timedelta(days=180)
    date_to = today

    try:

        fixtures = api_get(
            "fixtures",
            {
                "team": team_id,
                "from": date_from.strftime("%Y-%m-%d"),
                "to": date_to.strftime("%Y-%m-%d")
            }
        )

        # Ordena do mais recente para o mais antigo
        fixtures.sort(
            key=lambda item: item.get("fixture", {}).get("date", ""),
            reverse=True
        )

        return fixtures[:last]

    except Exception as error:

        raise RuntimeError(
            f"Não foi possível obter o histórico da equipe "
            f"{team_id}. Detalhes: {error}"
        )


# ==========================================================
# CÁLCULO DA FORMA
# ==========================================================

def calculate_team_form(team_id, last=10):

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

        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})

        home = teams.get("home", {})
        away = teams.get("away", {})

        home_id = home.get("id")
        away_id = away.get("id")

        home_goals = goals.get("home")
        away_goals = goals.get("away")

        # Ignora jogos sem resultado
        if home_goals is None or away_goals is None:
            continue

        # Equipe jogando em casa
        if team_id == home_id:

            team_goals = home_goals
            opponent_goals = away_goals

        # Equipe jogando fora
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

    # ======================================================
    # NENHUM JOGO ENCONTRADO
    # ======================================================

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

    # ======================================================
    # ÍNDICE DE FORMA
    # ======================================================

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


# ==========================================================
# TESTE DO PROVEDOR
# ==========================================================

if __name__ == "__main__":

    print("=" * 55)
    print("BET-AI - TESTE DO DATA PROVIDER")
    print("=" * 55)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"Data: {today}")
    print()

    try:

        games = get_real_games(today)

        print(
            f"Jogos encontrados hoje: {len(games)}"
        )

        for game in games[:5]:

            print(
                f"- {game['home']} x {game['away']}"
            )

        print()
        print("DATA PROVIDER funcionando.")

    except Exception as error:

        print()
        print("ERRO:")
        print(error)
        print("=" * 55)
        raise
