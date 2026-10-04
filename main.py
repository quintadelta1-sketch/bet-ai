import json
import os
from datetime import datetime, timezone

from data_provider import (
    get_real_games,
    calculate_team_form
)


VERSION = "BET-AI FINAL 2.2"


def load_json_games():
    """Carrega games.json como fonte de reserva."""
    if not os.path.exists("games.json"):
        return []

    try:
        with open("games.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("games", [])

    except Exception as error:
        print(f"Erro ao carregar games.json: {error}")

    return []


def clamp(value, minimum=0.05, maximum=0.95):
    """Mantém uma probabilidade dentro de limites razoáveis."""
    return max(minimum, min(maximum, value))


def calculate_probability(home_form, away_form):
    """
    Calcula uma probabilidade inicial usando:
    - forma recente;
    - vantagem de jogar em casa.
    """

    home_strength = (
        home_form["form"] * 0.65
        + 0.35
    )

    away_strength = (
        away_form["form"] * 0.65
    )

    total = home_strength + away_strength

    if total <= 0:
        return 50.0, 50.0

    home_probability = home_strength / total
    away_probability = away_strength / total

    home_probability = clamp(home_probability)
    away_probability = clamp(away_probability)

    # Normaliza novamente.
    total_probability = home_probability + away_probability

    home_probability = (
        home_probability / total_probability
    )

    away_probability = (
        away_probability / total_probability
    )

    return (
        round(home_probability * 100, 2),
        round(away_probability * 100, 2)
    )


def analyze_real_game(game):
    """Analisa uma partida usando histórico real."""

    home_id = game.get("home_id")
    away_id = game.get("away_id")

    if not home_id or not away_id:
        return {
            "home": game.get("home"),
            "away": game.get("away"),
            "error": "ID das equipes não encontrado."
        }

    print(
        f"Buscando histórico: "
        f"{game.get('home')} x {game.get('away')}"
    )

    try:
        home_form = calculate_team_form(
            home_id,
            last=10
        )

        away_form = calculate_team_form(
            away_id,
            last=10
        )

    except Exception as error:
        return {
            "home": game.get("home"),
            "away": game.get("away"),
            "error": f"Erro no histórico: {error}"
        }

    home_probability, away_probability = (
        calculate_probability(
            home_form,
            away_form
        )
    )

    return {
        "fixture_id": game.get("fixture_id"),

        "home": game.get("home"),
        "away": game.get("away"),

        "league": game.get("league"),
        "date": game.get("date"),

        "home_probability": home_probability,
        "away_probability": away_probability,

        "home_form": home_form,
        "away_form": away_form
    }


def print_analysis(result):
    """Mostra o resultado de maneira organizada."""

    print()
    print("=" * 55)

    print(
        f"{result.get('home', '?')} "
        f"x "
        f"{result.get('away', '?')}"
    )

    if result.get("league"):
        print(
            f"Competição: {result['league']}"
        )

    if result.get("error"):
        print(
            f"ERRO: {result['error']}"
        )
        print("=" * 55)
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

    print("=" * 55)


def main():

    print("=" * 55)
    print(VERSION)
    print("=" * 55)

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    games = []

    # ==================================================
    # 1. TENTA API-FOOTBALL
    # ==================================================

    try:

        print(
            f"Consultando API-Football: {today}"
        )

        real_games = get_real_games(today)

        if real_games:

            games = real_games

            print(
                "Fonte: API-Football"
            )

            print(
                f"Jogos encontrados: "
                f"{len(games)}"
            )

        else:

            print(
                "Nenhum jogo encontrado na API."
            )

    except Exception as error:

        print(
            f"Erro na API-Football: {error}"
        )

    # ==================================================
    # 2. MODO RESERVA
    # ==================================================

    if not games:

        games = load_json_games()

        if games:

            print(
                "Fonte: games.json "
                "(modo reserva)"
            )

            print(
                f"Jogos carregados: "
                f"{len(games)}"
            )

    # ==================================================
    # 3. NENHUM JOGO
    # ==================================================

    if not games:

        print(
            "Nenhum jogo disponível."
        )

        return

    # ==================================================
    # 4. ANALISAR JOGOS
    # ==================================================

    print()
    print(
        "INICIANDO ANÁLISE BET-AI"
    )

    resultados = []

    for game in games:

        try:

            result = analyze_real_game(
                game
            )

            resultados.append(
                result
            )

            print_analysis(
                result
            )

        except Exception as error:

            print()
            print(
                f"Erro analisando "
                f"{game.get('home', '?')} "
                f"x "
                f"{game.get('away', '?')}: "
                f"{error}"
            )

    # ==================================================
    # 5. RESUMO
    # ==================================================

    print()
    print("=" * 55)
    print("RESUMO BET-AI")
    print("=" * 55)

    print(
        f"Jogos analisados: "
        f"{len(resultados)}"
    )

    valid_results = [
        result
        for result in resultados
        if not result.get("error")
    ]

    print(
        f"Análises válidas: "
        f"{len(valid_results)}"
    )

    print()
    print(
        "BET-AI 2.2 concluído."
    )

    print("=" * 55)


if __name__ == "__main__":
    main()
