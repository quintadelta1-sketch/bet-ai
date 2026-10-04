import json
import os
from datetime import datetime, timezone

from data_provider import (
    get_real_games,
    calculate_team_form
)


VERSION = "BET-AI FINAL 2.3"

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

# Para respeitar o limite da API-Football
MAX_GAMES = 3

# Quantidade de jogos históricos por equipe
HISTORY_GAMES = 10


# ==========================================================
# CARREGAR GAMES.JSON
# ==========================================================

def load_json_games():

    if not os.path.exists("games.json"):
        return []

    try:

        with open(
            "games.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get(
                "games",
                []
            )

    except Exception as error:

        print(
            f"Erro ao carregar games.json: {error}"
        )

    return []


# ==========================================================
# LIMITAR PROBABILIDADE
# ==========================================================

def clamp(
    value,
    minimum=0.05,
    maximum=0.95
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ==========================================================
# CALCULAR PROBABILIDADE
# ==========================================================

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

    home_probability = clamp(
        home_probability
    )

    away_probability = clamp(
        away_probability
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
        round(
            home_probability * 100,
            2
        ),
        round(
            away_probability * 100,
            2
        )
    )


# ==========================================================
# ANÁLISE DE UM JOGO
# ==========================================================

def analyze_real_game(game):

    home_id = game.get(
        "home_id"
    )

    away_id = game.get(
        "away_id"
    )

    if not home_id or not away_id:

        return {

            "home": game.get(
                "home"
            ),

            "away": game.get(
                "away"
            ),

            "error":
                "ID das equipes não encontrado."

        }

    print()
    print(
        f"Analisando: "
        f"{game.get('home')} x "
        f"{game.get('away')}"
    )

    print(
        f"Histórico casa "
        f"(ID {home_id})..."
    )

    try:

        home_form = calculate_team_form(
            home_id,
            last=HISTORY_GAMES
        )

    except Exception as error:

        return {

            "home": game.get(
                "home"
            ),

            "away": game.get(
                "away"
            ),

            "error":
                f"Erro no histórico: {error}"

        }

    print(
        f"Histórico fora "
        f"(ID {away_id})..."
    )

    try:

        away_form = calculate_team_form(
            away_id,
            last=HISTORY_GAMES
        )

    except Exception as error:

        return {

            "home": game.get(
                "home"
            ),

            "away": game.get(
                "away"
            ),

            "error":
                f"Erro no histórico: {error}"

        }

    # ------------------------------------------------------
    # PROBABILIDADES
    # ------------------------------------------------------

    (
        home_probability,
        away_probability
    ) = calculate_probability(
        home_form,
        away_form
    )

    # ------------------------------------------------------
    # RESULTADO
    # ------------------------------------------------------

    return {

        "fixture_id":
            game.get(
                "fixture_id"
            ),

        "home":
            game.get(
                "home"
            ),

        "away":
            game.get(
                "away"
            ),

        "league":
            game.get(
                "league"
            ),

        "date":
            game.get(
                "date"
            ),

        "home_probability":
            home_probability,

        "away_probability":
            away_probability,

        "home_form":
            home_form,

        "away_form":
            away_form

    }


# ==========================================================
# EXIBIR ANÁLISE
# ==========================================================

def print_analysis(result):

    print()
    print(
        "=" * 60
    )

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

    # ------------------------------------------------------
    # ERRO
    # ------------------------------------------------------

    if result.get("error"):

        print()
        print(
            f"ERRO: "
            f"{result['error']}"
        )

        print(
            "=" * 60
        )

        return

    # ------------------------------------------------------
    # PROBABILIDADES
    # ------------------------------------------------------

    print()

    print(
        f"Probabilidade Casa: "
        f"{result['home_probability']}%"
    )

    print(
        f"Probabilidade Fora: "
        f"{result['away_probability']}%"
    )

    home = result[
        "home_form"
    ]

    away = result[
        "away_form"
    ]

    # ------------------------------------------------------
    # CASA
    # ------------------------------------------------------

    print()

    print(
        "FORMA - CASA"
    )

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

    # ------------------------------------------------------
    # FORA
    # ------------------------------------------------------

    print()

    print(
        "FORMA - FORA"
    )

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

    print(
        "=" * 60
    )


# ==========================================================
# SELECIONAR JOGOS
# ==========================================================

def select_games(games):

    selected = []

    used_teams = set()

    for game in games:

        home_id = game.get(
            "home_id"
        )

        away_id = game.get(
            "away_id"
        )

        if not home_id or not away_id:
            continue

        # Evita repetir equipe
        if home_id in used_teams:
            continue

        if away_id in used_teams:
            continue

        selected.append(
            game
        )

        used_teams.add(
            home_id
        )

        used_teams.add(
            away_id
        )

        if len(selected) >= MAX_GAMES:
            break

    return selected


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():

    print(
        "=" * 60
    )

    print(
        VERSION
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Limite de análise:",
        MAX_GAMES,
        "jogos"
    )

    print(
        "Histórico por equipe:",
        HISTORY_GAMES,
        "jogos"
    )

    # ------------------------------------------------------
    # DATA
    # ------------------------------------------------------

    today = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d"
    )

    print()

    print(
        f"Data consultada: {today}"
    )

    # ------------------------------------------------------
    # BUSCAR JOGOS REAIS
    # ------------------------------------------------------

    games = []

    try:

        print()

        print(
            "Consultando API-Football..."
        )

        real_games = get_real_games(
            today
        )

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
                "Nenhum jogo encontrado "
                "na API para hoje."
            )

    except Exception as error:

        print()

        print(
            f"Erro na API-Football: "
            f"{error}"
        )

    # ------------------------------------------------------
    # MODO RESERVA
    # ------------------------------------------------------

    if not games:

        games = load_json_games()

        if games:

            print()

            print(
                "Fonte: games.json "
                "(modo reserva)"
            )

            print(
                f"Jogos carregados: "
                f"{len(games)}"
            )

    # ------------------------------------------------------
    # NENHUM JOGO
    # ------------------------------------------------------

    if not games:

        print()

        print(
            "Nenhum jogo disponível."
        )

        return

    # ------------------------------------------------------
    # SELEÇÃO
    # ------------------------------------------------------

    selected_games = select_games(
        games
    )

    print()

    print(
        f"Jogos selecionados para "
        f"análise: {len(selected_games)}"
    )

    # ------------------------------------------------------
    # ANÁLISE
    # ------------------------------------------------------

    print()

    print(
        "INICIANDO ANÁLISE BET-AI"
    )

    resultados = []

    for game in selected_games:

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

    # ------------------------------------------------------
    # RESUMO
    # ------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "RESUMO BET-AI"
    )

    print(
        "=" * 60
    )

    print(
        f"Jogos encontrados: "
        f"{len(games)}"
    )

    print(
        f"Jogos selecionados: "
        f"{len(selected_games)}"
    )

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

    errors = [
        result
        for result in resultados
        if result.get("error")
    ]

    print(
        f"Análises com erro: "
        f"{len(errors)}"
    )

    # ------------------------------------------------------
    # MELHOR OPORTUNIDADE
    # ------------------------------------------------------

    if valid_results:

        best = max(
            valid_results,
            key=lambda result: max(
                result["home_probability"],
                result["away_probability"]
            )
        )

        print()

        print(
            "MAIOR PROBABILIDADE ENCONTRADA"
        )

        print(
            f"{best['home']} "
            f"x "
            f"{best['away']}"
        )

        print(
            f"Casa: "
            f"{best['home_probability']}%"
        )

        print(
            f"Fora: "
            f"{best['away_probability']}%"
        )

    print()

    print(
        "BET-AI 2.3 concluído."
    )

    print(
        "=" * 60
    )


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    main()
