import os
import requests


API_URL = "https://v3.football.api-sports.io"


def get_headers():
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        raise RuntimeError("API_FOOTBALL_KEY não configurada.")

    return {
        "x-apisports-key": api_key
    }


def get_fixtures(date):
    response = requests.get(
        f"{API_URL}/fixtures",
        headers=get_headers(),
        params={"date": date},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", [])


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
