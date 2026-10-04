import json
import os
from datetime import datetime, timezone

from data_provider import get_real_games


VERSION = "BET-AI FINAL 2.0"


def load_json_games():
    """Carrega jogos locais como modo de reserva."""
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


def prepare_real_game(game):
    """
    Converte um jogo da API para o formato usado pelo
    analisador do BET-AI.
    """

    return {
        "fixture_id": game.get("fixture_id"),
        "home": game.get("home"),
        "away": game.get("away"),

        # Ainda não temos essas estatísticas para todos os jogos.
        # Elas serão preenchidas na próxima etapa.
        "home_form": 0.50,
        "away_form": 0.50,

        "home_strength": 0.50,
        "away_strength": 0.50,

        "home_avg_goals": 1.50,
        "away_avg_goals": 1.50,

        "league": game.get("league"),
        "date": game.get("date"),
    }


def analyze_game(game):
    home = (
        game["home_form"] * 0.35
        + game["home_strength"] * 0.35
        + min(game["home_avg_goals"] / 2.5, 1) * 0.30
    )

    away = (
        game["away_form"] * 0.35
        + game["away_strength"] * 0.35
        + min(game["away_avg_goals"] / 2.5, 1) * 0.30
    )

    total = home + away

    if total == 0:
        home_prob = 0.50
        away_prob = 0.50
    else:
        home_prob = home / total
        away_prob = away / total

    return {
        "fixture_id": game.get("fixture_id"),
        "home": game["home"],
        "away": game["away"],
        "league": game.get("league"),

        "home_probability": round(home_prob * 100, 2),
        "away_probability": round(away_prob * 100, 2),
    }


def main():
    print("=" * 50)
    print(VERSION)
    print("=" * 50)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    games = []

    # Tenta primeiro os dados reais.
    try:
        print(f"Consultando API-Football: {today}")

        real_games = get_real_games(today)

        if real_games:
            games = [
                prepare_real_game(game)
                for game in real_games
            ]

            print(f"Fonte: API-Football")
            print(f"Jogos encontrados: {len(games)}")

        else:
            print("API sem jogos disponíveis para a data.")

    except Exception as error:
        print(f"Falha na API-Football: {error}")

    # Se a API falhar ou não encontrar jogos,
    # usa games.json como reserva.
    if not games:
        games = load_json_games()

        if games:
            print("Fonte: games.json (reserva)")
            print(f"Jogos carregados: {len(games)}")

    if not games:
        print("Nenhum jogo disponível.")
        return

    print()
    print("ANÁLISE DOS JOGOS")
    print("-" * 50)

    for game in games:
        try:
            result = analyze_game(game)

            print()
            print(
                f"{result['home']} x {result['away']}"
            )

            if result.get("league"):
                print(f"Competição: {result['league']}")

            print(
                f"Casa: {result['home_probability']}%"
            )

            print(
                f"Fora: {result['away_probability']}%"
            )

        except Exception as error:
            print(
                f"Erro analisando "
                f"{game.get('home', '?')} x "
                f"{game.get('away', '?')}: {error}"
            )

    print()
    print("-" * 50)
    print("Análise concluída.")
    print("=" * 50)


if __name__ == "__main__":
    main()
