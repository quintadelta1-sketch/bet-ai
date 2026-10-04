import json
import os
from datetime import datetime, timezone

from data_provider import (
    get_real_games,
    calculate_team_form
)


VERSION = "BET-AI FINAL 2.4"

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MAX_GAMES = 2

HISTORY_GAMES = 10


# ==========================================================
# GAMES.JSON
# ==========================================================

def load_json_games():

    if not os.path.exists(
        "games.json"
    ):

        return []

    try:

        with open(
            "games.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        if isinstance(
            data,
            list
        ):

            return data

        if isinstance(
            data,
            dict
        ):

            return data.get(
                "games",
                []
            )

    except Exception as error:

        print(
            f"Erro no games.json: "
            f"{error}"
        )

    return []


# ==========================================================
# PROBABILIDADE
# ==========================================================

def calculate_probability(
    home_form,
    away_form
):

    home_strength = (
        home_form["form"]
        * 0.65
        + 0.35
    )

    away_strength = (
        away_form["form"]
        * 0.65
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
# ANALISAR JOGO
# ==========================================================

def analyze_game(
    game
):

    home = game.get(
        "home"
    )

    away = game.get(
        "away"
    )

    home_id = game.get(
        "home_id"
    )

    away_id = game.get(
        "away_id"
    )

    print()

    print(
        "-" * 60
    )

    print(
        f"{home} x {away}"
    )

    print(
        "-" * 60
    )

    if not home_id or not away_id:

        return {

            "home": home,

            "away": away,

            "error":
                "ID das equipes não encontrado."
        }

    # ------------------------------------------------------
    # CASA
    # ------------------------------------------------------

    print(
        f"Buscando histórico: {home}"
    )

    try:

        home_form = calculate_team_form(
            home_id,
            HISTORY_GAMES
        )

    except Exception as error:

        return {

            "home": home,

            "away": away,

            "error":
                f"Erro no histórico: {error}"
        }

    # ------------------------------------------------------
    # FORA
    # ------------------------------------------------------

    print(
        f"Buscando histórico: {away}"
    )

    try:

        away_form = calculate_team_form(
            away_id,
            HISTORY_GAMES
        )

    except Exception as error:

        return {

            "home": home,

            "away": away,

            "error":
                f"Erro no histórico: {error}"
        }

    # ------------------------------------------------------
    # PROBABILIDADE
    # ------------------------------------------------------

    (
        home_probability,
        away_probability
    ) = calculate_probability(
        home_form,
        away_form
    )

    return {

        "fixture_id":
            game.get(
                "fixture_id"
            ),

        "home":
            home,

        "away":
            away,

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
# EXIBIR RESULTADO
# ==========================================================

def print_result(
    result
):

    print()

    print(
        "=" * 60
    )

    print(
        f"{result.get('home', '?')} "
        f"x "
        f"{result.get('away', '?')}"
    )

    if result.get(
        "error"
    ):

        print()

        print(
            result["error"]
        )

        print(
            "=" * 60
        )

        return

    print()

    print(
        f"Casa: "
        f"{result['home_probability']}%"
    )

    print(
        f"Fora: "
        f"{result['away_probability']}%"
    )

    home = result[
        "home_form"
    ]

    away = result[
        "away_form"
    ]

    print()

    print(
        "FORMA DA CASA"
    )

    print(
        f"Jogos: {home['played']} | "
        f"V: {home['wins']} | "
        f"E: {home['draws']} | "
        f"D: {home['losses']}"
    )

    print(
        f"Média gols marcados: "
        f"{home['goals_for_avg']}"
    )

    print(
        f"Média gols sofridos: "
        f"{home['goals_against_avg']}"
    )

    print()

    print(
        "FORMA DO FORA"
    )

    print(
        f"Jogos: {away['played']} | "
        f"V: {away['wins']} | "
        f"E: {away['draws']} | "
        f"D: {away['losses']}"
    )

    print(
        f"Média gols marcados: "
        f"{away['goals_for_avg']}"
    )

    print(
        f"Média gols sofridos: "
        f"{away['goals_against_avg']}"
    )

    print(
        "=" * 60
    )


# ==========================================================
# SELECIONAR JOGOS
# ==========================================================

def select_games(
    games
):

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
# MAIN
# ==========================================================

def main():

    print()

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
        "Modo econômico da API: ATIVO"
    )

    print(
        f"Máximo de jogos: "
        f"{MAX_GAMES}"
    )

    print(
        f"Histórico por equipe: "
        f"{HISTORY_GAMES}"
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
        f"Data consultada: "
        f"{today}"
    )

    # ------------------------------------------------------
    # JOGOS
    # ------------------------------------------------------

    games = []

    try:

        print()

        print(
            "Consultando jogos do dia..."
        )

        games = get_real_games(
            today
        )

        print(
            f"Jogos encontrados: "
            f"{len(games)}"
        )

    except Exception as error:

        print()

        print(
            f"Erro ao buscar jogos: "
            f"{error}"
        )

    # ------------------------------------------------------
    # RESERVA
    # ------------------------------------------------------

    if not games:

        games = load_json_games()

        if games:

            print()

            print(
                "Usando games.json "
                "como reserva."
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
        f"Jogos selecionados: "
        f"{len(selected_games)}"
    )

    # ------------------------------------------------------
    # ANALISAR
    # ------------------------------------------------------

    results = []

    for game in selected_games:

        result = analyze_game(
            game
        )

        results.append(
            result
        )

        print_result(
            result
        )

    # ------------------------------------------------------
    # RESUMO
    # ------------------------------------------------------

    valid = [
        result
        for result in results
        if not result.get(
            "error"
        )
    ]

    errors = [
        result
        for result in results
        if result.get(
            "error"
        )
    ]

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
        f"Análises válidas: "
        f"{len(valid)}"
    )

    print(
        f"Análises com erro: "
        f"{len(errors)}"
    )

    if valid:

        print()

        print(
            "ANÁLISES CONCLUÍDAS"
        )

        for result in valid:

            print()

            print(
                f"{result['home']} "
                f"x "
                f"{result['away']}"
            )

            print(
                f"Casa: "
                f"{result['home_probability']}%"
            )

            print(
                f"Fora: "
                f"{result['away_probability']}%"
            )

    print()

    print(
        "BET-AI 2.4 concluído."
    )

    print(
        "=" * 60
    )


# ==========================================================
# EXECUTAR
# ==========================================================

if __name__ == "__main__":

    main()
