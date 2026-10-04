import os
from datetime import datetime, timezone

from data_provider import (
    get_real_games,
    calculate_team_form
)


VERSION = "BET-AI FINAL 3.0"


# ============================================================
# CONFIGURAÇÕES
# ============================================================

# Para proteger o limite da API.
MAX_GAMES = 1

# Número de jogos históricos usados para calcular a forma.
HISTORY_GAMES = 10


# ============================================================
# PROBABILIDADES
# ============================================================

def calculate_probability(
    home_form,
    away_form
):

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

    # Limites conservadores
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

    home_probability = (
        home_probability
        / total_probability
    )

    away_probability = (
        away_probability
        / total_probability
    )

    return (
        round(home_probability * 100, 2),
        round(away_probability * 100, 2)
    )


# ============================================================
# ANÁLISE
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

    if not home_id or not away_id:

        return {
            "home": home_name,
            "away": away_name,
            "error": "ID das equipes não encontrado."
        }

    print()
    print(
        f"Analisando: "
        f"{home_name} x {away_name}"
    )

    print(
        f"Buscando últimos "
        f"{HISTORY_GAMES} jogos da equipe da casa..."
    )

    try:

        home_form = calculate_team_form(
            home_id,
            last=HISTORY_GAMES
        )

    except Exception as error:

        return {
            "home": home_name,
            "away": away_name,
            "error": (
                "Erro no histórico da "
                f"equipe {home_id}: {error}"
            )
        }

    print(
        f"Buscando últimos "
        f"{HISTORY_GAMES} jogos da equipe visitante..."
    )

    try:

        away_form = calculate_team_form(
            away_id,
            last=HISTORY_GAMES
        )

    except Exception as error:

        return {
            "home": home_name,
            "away": away_name,
            "error": (
                "Erro no histórico da "
                f"equipe {away_id}: {error}"
            )
        }

    (
        home_probability,
        away_probability
    ) = calculate_probability(
        home_form,
        away_form
    )

    return {

        "fixture_id":
            game.get("fixture_id"),

        "home":
            home_name,

        "away":
            away_name,

        "league":
            game.get("league"),

        "date":
            game.get("date"),

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
# IMPRESSÃO
# ============================================================

def print_analysis(result):

    print()
    print("=" * 60)

    print(
        f"{result.get('home', '?')} "
        f"x "
        f"{result.get('away', '?')}"
    )

    if result.get("league"):

        print(
            f"Competição: "
            f"{result['league']}"
        )

    if result.get("error"):

        print()
        print(
            f"ERRO: "
            f"{result['error']}"
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
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print(VERSION)
    print("=" * 60)

    api_key = os.getenv(
        "API_FOOTBALL_KEY"
    )

    if not api_key:

        print()
        print(
            "ERRO: API_FOOTBALL_KEY não encontrada."
        )

        print(
            "Verifique o Secret do GitHub."
        )

        return

    # Data atual em UTC
    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    print()
    print(
        f"Data consultada: {today}"
    )

    print(
        "Consultando jogos reais..."
    )

    # ========================================================
    # 1 - BUSCAR JOGOS DO DIA
    # ========================================================

    try:

        games = get_real_games(
            today
        )

    except Exception as error:

        print()
        print(
            "ERRO AO CONSULTAR "
            "API-FOOTBALL:"
        )

        print(error)

        print()
        print(
            "A execução foi encerrada "
            "para evitar gastar mais requisições."
        )

        return

    if not games:

        print()
        print(
            "Nenhum jogo encontrado "
            "para esta data."
        )

        return

    # ========================================================
    # 2 - LIMITAR JOGOS
    # ========================================================

    games = games[:MAX_GAMES]

    print()
    print(
        f"Jogos encontrados: "
        f"{len(games)}"
    )

    print(
        f"Jogos selecionados para análise: "
        f"{len(games)}"
    )

    # ========================================================
    # 3 - ANALISAR
    # ========================================================

    resultados = []

    for game in games:

        result = analyze_game(
            game
        )

        resultados.append(
            result
        )

        print_analysis(
            result
        )

        # Se a API acusar limite,
        # não tenta outro jogo.
        if result.get("error"):

            if "limite" in result["error"].lower():

                print()
                print(
                    "Limite da API detectado."
                )

                print(
                    "Encerrando execução."
                )

                break

    # ========================================================
    # 4 - RESUMO
    # ========================================================

    print()
    print("=" * 60)
    print("RESUMO BET-AI")
    print("=" * 60)

    print(
        f"Jogos processados: "
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
        "BET-AI FINAL 3.0 concluído."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
