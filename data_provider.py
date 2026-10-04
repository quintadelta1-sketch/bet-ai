import os
import requests


API_URL = "https://v3.football.api-sports.io"


def get_headers():
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada."
        )

    return {
        "x-apisports-key": api_key,
        "Accept": "application/json"
    }


def get_fixtures(date):
    url = f"{API_URL}/fixtures"

    params = {
        "date": date
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", [])


def get_fixture(fixture_id):
    url = f"{API_URL}/fixtures"

    params = {
        "id": fixture_id
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    response_data = data.get("response", [])

    if not response_data:
        return None

    return response_data[0]


def normalize_fixture(fixture):
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})

    home = teams.get("home", {})
    away = teams.get("away", {})

    return {
        "fixture_id": fixture.get("fixture", {}).get("id"),

        "home": home.get("name"),
        "away": away.get("name"),

        "home_id": home.get("id"),
        "away_id": away.get("id"),

        "home_goals": goals.get("home"),
        "away_goals": goals.get("away"),

        "league": fixture.get("league", {}).get("name"),
        "season": fixture.get("league", {}).get("season"),

        "date": fixture.get("fixture", {}).get("date")
    }
