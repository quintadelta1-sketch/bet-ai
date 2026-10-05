import os
from datetime import datetime, timezone

from data_provider import (
    get_real_games,
    calculate_team_form
)


VERSION = "BET-AI FINAL 3.2"

MAX_GAMES = 1
HISTORY_GAMES = 10


# ============================================================
# PROBABILIDADE
# ============================================================

def calculate_probability(home_form, away_form):

    home_strength = (
        home_form["form"] * 0.65
        + 0.35
    )

    away_strength = (
        away_form["form"] * 0.65
    )

    total = (
        home_strength
        + away_strength
    )

    if total <= 0:
        return 50.0, 50.0

    home_probability = (
        home_strength / total
    )

    away_probability = (
        away_strength / total
    )

    home_probability = max(
        0.05,
        min(0.95, home_probability)
    )

    away_probability = max(
        0.05,
        min(0.95, away_probability)
    )

    total_probability = (
        home_probability
        + away_probability
    )

    home_probability /= total_probability
    away_probability /= total_probability

    return (
        round(home_probability * 100, 2),
        round(away_probability * 100, 2)
    )


# ============================================================
# ANÁLISE DO JOGO
# ============================================================

def analyze_game(game):

    home_id = game.get("home_id")
    away_id = game.get("away_id")

    home_name = game.get(
        "home",
        "Casa"
    )

    away_name = game.get(
        "away",
        "Fora"
    )

    season = game.get("season")

    if not home_id or not away_id:

        return {
            "home": home_name,
            "away": away_name,
            "error": "ID das equipes não encontrado."
        }

    if not season:

        return {
            "home": home_name,
            "away": away_name,
            "error": "Temporada do jogo não encontrada."
        }

    print()
    print(
        f"Analisando: {home_name} x {away_name}"
    )

    print(
        f"Temporada identificada: {season}"
    )

    try:

        print(
            "Buscando histórico da equipe da casa..."
        )

        home_form = calculate_team_form(
            home_id,
            games_required=HISTORY_GAMES,
            season=season
        )

        print(
            "Histórico da equipe da casa obtido."
        )

        print(
            "Buscando histórico da equipe visitante..."
        )

        away_form = calculate_team_form(
            away_id,
            games_required=HISTORY_GAMES,
            season=season
        )

        print(
            "Histórico da equipe visitante obtido."
        )

    except Exception as error:

        return {
            "home": home_name,
            "away": away_name,
            "error": str(error)
        }

    home_probability, away_probability = (
        calculate_probability(
            home_form,
            away_form
        )
    )

    return {

        "fixture_id": game.get(
            "fixture_id"
        ),

        "home": home_name,
        "away": away_name,

        "league": game.get(
            "league"
        ),

        "date": game.get(
            "date"
        ),

        "season": season,

        "home_probability":
            home_probability,

        "away_probability":
            away_probability,

        "home_form":
            home_form,

        "away_form":
            away_form
    }


# ============================================================
# IMPRESSÃO DA ANÁLISE
# ============================================================

def print_analysis(result):

    print()
    print("=" * 60)

    print(
        f"{result.get('home', '?')} x "
        f"{result.get('away', '?')}"
    )

    if result.get("league"):

        print(
            f"Competição: "
            f"{result['league']}"
        )

    if result.get("season"):

        print(
            f"Temporada: "
            f"{result['season']}"
        )

    if result.get("error"):

        print()
        print(
            f"ERRO: {result['error']}"
        )

        print("=" * 60)

        return

    print()

    print(
        f"Probabilidade Casa: "
        f"{result['home_probability']}%"
    )

    print(
        f"Probabilidade Fora: "
        f"{result['away_probability']}%"
    )

    home = result["home_form"]
    away = result["away_form"]

    print()
    print("FORMA - CASA")

    print(
        f"Jogos: {home['played']} | "
        f"V: {home['wins']} | "
        f"E: {home['draws']} | "
        f"D: {home['losses']}"
    )

    print(
        f"Gols marcados/jogo: "
        f"{home['goals_for_avg']}"
    )

    print(
        f"Gols sofridos/jogo: "
        f"{home['goals_against_avg']}"
    )

    print(
        f"Índice de forma: "
        f"{round(home['form'] * 100, 2)}%"
    )

    print()
    print("FORMA - FORA")

    print(
        f"Jogos: {away['played']} | "
        f"V: {away['wins']} | "
        f"E: {away['draws']} | "
        f"D: {away['losses']}"
    )

    print(
        f"Gols marcados/jogo: "
        f"{away['goals_for_avg']}"
    )

    print(
        f"Gols sofridos/jogo: "
        f"{away['goals_against_avg']}"
    )

    print(
        f"Índice de forma: "
        f"{round(away['form'] * 100, 2)}%"
    )

    print("=" * 60)


# ============================================================
# PRINCIPAL
# ============================================================

def main():

    print("=" * 60)

    print(VERSION)

    print("=" * 60)

    api_key = os.getenv(
        "API_FOOTBALL_KEY"
    )

    if not api_key:

        print(
            "ERRO: API_FOOTBALL_KEY não encontrada."
        )

        return

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    print()

    print(
        f"Consultando jogos do dia: {today}"
    )

    try:

        games = get_real_games(
            today
        )

    except Exception as error:

        print()

        print(
            f"ERRO AO CONSULTAR API: "
            f"{error}"
        )

        return

    if not games:

        print(
            "Nenhum jogo encontrado."
        )

        return

    games = games[:MAX_GAMES]

    print()

    print(
        f"Jogos selecionados: "
        f"{len(games)}"
    )

    results = []

    for game in games:

        result = analyze_game(
            game
        )

        results.append(
            result
        )

        print_analysis(
            result
        )

    print()

    print("=" * 60)

    print("RESUMO BET-AI")

    print("=" * 60)

    valid = [
        result
        for result in results
        if not result.get("error")
    ]

    print(
        f"Jogos processados: "
        f"{len(results)}"
    )

    print(
        f"Análises válidas: "
        f"{len(valid)}"
    )

    print()

    print(
        "BET-AI FINAL 3.2 concluído."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
