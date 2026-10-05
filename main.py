from datetime import datetime, timezone

from config import (
    VERSION,
    MAX_GAMES
)

from data_provider import (
    get_real_games
)

from analyzer import (
    analyze_game
)

from ticket import (
    generate_ticket,
    print_ticket
)


# ============================================================
# IMPRESSÃO DA FORMA
# ============================================================

def print_form(
    title,
    form
):

    print()
    print(title)

    print(
        f"Jogos: {form['played']}"
    )

    print(
        f"Vitórias: {form['wins']}"
    )

    print(
        f"Empates: {form['draws']}"
    )

    print(
        f"Derrotas: {form['losses']}"
    )

    print(
        f"Gols marcados/jogo: "
        f"{form['goals_for_avg']}"
    )

    print(
        f"Gols sofridos/jogo: "
        f"{form['goals_against_avg']}"
    )

    print(
        f"Pontos/jogo: "
        f"{form['points_per_game']}"
    )

    print(
        f"Forma: "
        f"{round(form['form'] * 100, 2)}%"
    )


# ============================================================
# IMPRESSÃO DOS MERCADOS
# ============================================================

def print_markets(
    analysis
):

    print()
    print(
        "MERCADOS"
    )

    print("-" * 60)

    for market in analysis[
        "markets"
    ]:

        print(
            f"{market['market']}: "
            f"{market['probability']}% "
            f"[{market['classification']}]"
        )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 60)

    print(VERSION)

    print("=" * 60)

    today = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d"
    )

    print()
    print(
        f"Consultando jogos do dia: "
        f"{today}"
    )

    # --------------------------------------------------------
    # JOGOS
    # --------------------------------------------------------

    try:

        games = get_real_games(
            today
        )

    except Exception as error:

        print()
        print(
            f"ERRO AO BUSCAR JOGOS: "
            f"{error}"
        )

        return

    if not games:

        print()
        print(
            "Nenhum jogo encontrado."
        )

        return

    # --------------------------------------------------------
    # LIMITA JOGOS
    # --------------------------------------------------------

    games = games[
        :MAX_GAMES
    ]

    print()
    print(
        f"Jogos selecionados: "
        f"{len(games)}"
    )

    successful = 0

    # --------------------------------------------------------
    # ANALISAR
    # --------------------------------------------------------

    for game in games:

        print()
        print("=" * 60)

        try:

            analysis = analyze_game(
                game
            )

            # -----------------------------------------------
            # RESULTADO
            # -----------------------------------------------

            print()
            print("=" * 60)

            print(
                f"{analysis['home']} x "
                f"{analysis['away']}"
            )

            print(
                f"Competição: "
                f"{analysis['league']}"
            )

            print(
                f"Temporada: "
                f"{analysis['season']}"
            )

            print("=" * 60)

            # -----------------------------------------------
            # FORMA
            # -----------------------------------------------

            print_form(
                "FORMA - CASA",
                analysis["home_form"]
            )

            print_form(
                "FORMA - FORA",
                analysis["away_form"]
            )

            # -----------------------------------------------
            # GOLS
            # -----------------------------------------------

            print()

            print(
                "EXPECTATIVA DE GOLS"
            )

            print(
                f"Casa: "
                f"{analysis['expected_home_goals']}"
            )

            print(
                f"Fora: "
                f"{analysis['expected_away_goals']}"
            )

            print(
                f"Total: "
                f"{analysis['expected_total_goals']}"
            )

            # -----------------------------------------------
            # MERCADOS
            # -----------------------------------------------

            print_markets(
                analysis
            )

            # -----------------------------------------------
            # BILHETE
            # -----------------------------------------------

            ticket = generate_ticket(
                analysis
            )

            print_ticket(
                analysis,
                ticket
            )

            successful += 1

        except Exception as error:

            print()
            print(
                f"ERRO NA ANÁLISE: "
                f"{error}"
            )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print()
    print("=" * 60)

    print(
        "RESUMO BET-AI V4"
    )

    print("=" * 60)

    print(
        f"Jogos selecionados: "
        f"{len(games)}"
    )

    print(
        f"Análises concluídas: "
        f"{successful}"
    )

    print()

    print(
        "BET-AI V4 FINALIZADO."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
