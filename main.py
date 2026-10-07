from config import (
    MAX_GAMES,
    CANDIDATE_GAMES,
    get_analysis_date,
)

from data_provider import (
    get_upcoming_games,
    get_prediction,
    get_odds,
    update_finished_fixtures,
)

from analyzer import analyze_game

from ticket import generate_ticket

from memory import (
    load_memory,
    save_memory,
    get_pending_fixture_ids,
    update_memory_with_results,
    register_prediction,
    memory_summary,
)


def print_separator():

    print()
    print(
        "=" * 70
    )


def print_market(
    market
):

    probability = market.get(
        "probability"
    )

    edge = market.get(
        "edge"
    )

    odd = market.get(
        "odd"
    )

    classification = market.get(
        "classification"
    )

    line = (
        f"{market.get('name')}: "
        f"{probability:.2f}%"
    )

    if odd:
        line += (
            f" | Odd {odd:.2f}"
        )

    if edge is not None:
        line += (
            f" | Edge {edge:.2f}%"
        )

    line += (
        f" | {classification}"
    )

    print(line)


def print_learning(
    memory
):

    summary = memory_summary(
        memory
    )

    print_separator()

    print(
        "MEMÓRIA DO BET-AI"
    )

    print(
        f"Previsões armazenadas: "
        f"{summary['total_predictions']}"
    )

    print(
        f"Partidas avaliadas: "
        f"{summary['completed']}"
    )

    print(
        f"Partidas pendentes: "
        f"{summary['pending']}"
    )

    learning = summary[
        "learning"
    ]

    if not learning:

        print(
            "Ainda não existe histórico "
            "suficiente para recalibração."
        )

        return

    print()

    print(
        "DESEMPENHO POR MERCADO:"
    )

    ordered = sorted(
        learning.items(),
        key=lambda item: (
            item[1]["accuracy"]
        ),
        reverse=True
    )

    for key, stats in ordered:

        print(
            f"- {key}: "
            f"{stats['accuracy']:.1f}% "
            f"({stats['hits']}/"
            f"{stats['total']})"
        )


def main():

    print_separator()

    print(
        "BET-AI"
    )

    print(
        "Motor adaptativo de análise "
        "de futebol"
    )

    print_separator()

    memory = load_memory()

    # ------------------------------------------------
    # 1. ATUALIZAR RESULTADOS ANTIGOS
    # ------------------------------------------------

    pending_ids = (
        get_pending_fixture_ids(
            memory
        )
    )

    if pending_ids:

        fixtures = update_finished_fixtures(
            pending_ids
        )

        if fixtures:

            updated = (
                update_memory_with_results(
                    memory,
                    fixtures
                )
            )

            print(
                f"Resultados atualizados: "
                f"{updated}"
            )

            save_memory(
                memory
            )

    # ------------------------------------------------
    # 2. BUSCAR PRÓXIMOS JOGOS
    # ------------------------------------------------

    games = get_upcoming_games()

    if not games:

        print()
        print(
            "Nenhum jogo futuro encontrado."
        )

        print_learning(
            memory
        )

        save_memory(
            memory
        )

        return

    # ------------------------------------------------
    # 3. SELECIONAR ATÉ 3 JOGOS COM PREVISÃO
    # ------------------------------------------------

    selected_games = []

    for game in games[
        :CANDIDATE_GAMES
    ]:

        if len(
            selected_games
        ) >= MAX_GAMES:

            break

        fixture_id = game[
            "fixture_id"
        ]

        if any(
            x["fixture_id"]
            == fixture_id
            for x in selected_games
        ):
            continue

        print_separator()

        print(
            f"Testando previsão: "
            f"{game['home_name']} "
            f"x "
            f"{game['away_name']}"
        )

        prediction = get_prediction(
            fixture_id
        )

        if not prediction:

            print(
                "Sem previsão disponível."
            )

            continue

        selected_games.append({
            "game": game,
            "prediction": prediction,
        })

    if not selected_games:

        print_separator()

        print(
            "Nenhum dos jogos candidatos "
            "possui previsão disponível."
        )

        print_learning(
            memory
        )

        save_memory(
            memory
        )

        return

    # ------------------------------------------------
    # 4. ANALISAR OS 3 JOGOS
    # ------------------------------------------------

    analyzed_count = 0

    for item in selected_games:

        game = item[
            "game"
        ]

        prediction = item[
            "prediction"
        ]

        fixture_id = game[
            "fixture_id"
        ]

        print_separator()

        print(
            f"ANÁLISE "
            f"{analyzed_count + 1}/"
            f"{len(selected_games)}"
        )

        print(
            f"{game['home_name']} "
            f"x "
            f"{game['away_name']}"
        )

        print(
            f"Competição: "
            f"{game['league_name']}"
        )

        print(
            f"Fixture ID: "
            f"{fixture_id}"
        )

        print()

        # --------------------------------------------
        # ODDS
        # --------------------------------------------

        odds = get_odds(
            game
        )

        # --------------------------------------------
        # ANÁLISE
        # --------------------------------------------

        try:

            analysis = analyze_game(
                game,
                prediction,
                odds,
                memory
            )

        except Exception as error:

            print(
                "Erro na análise: "
                f"{error}"
            )

            continue

        # --------------------------------------------
        # RESULTADO DA ANÁLISE
        # --------------------------------------------

        print()

        print(
            f"Vencedor previsto: "
            f"{analysis['winner']}"
        )

        print(
            f"Comentário: "
            f"{analysis['winner_comment']}"
        )

        print(
            f"Conselho da API: "
            f"{analysis['advice']}"
        )

        print(
            f"Previsão gols API: "
            f"{analysis['api_under_over']}"
        )

        expected = analysis[
            "expected_goals"
        ]

        if expected["total"] is not None:

            print(
                f"Gols estimados: "
                f"{expected['home']:.2f} "
                f"x "
                f"{expected['away']:.2f} "
                f"(total "
                f"{expected['total']:.2f})"
            )

        print()

        print(
            "MERCADOS:"
        )

        for market in analysis[
            "markets"
        ]:

            print_market(
                market
            )

        # --------------------------------------------
        # BILHETE
        # --------------------------------------------

        ticket = generate_ticket(
            analysis["markets"]
        )

        print()

        print(
            f"MODO DO BILHETE: "
            f"{ticket['mode']}"
        )

        if not ticket[
            "selections"
        ]:

            print(
                "Nenhuma seleção atingiu "
                "os critérios."
            )

        else:

            for selection in ticket[
                "selections"
            ]:

                print(
                    f"→ "
                    f"{selection['name']} | "
                    f"{selection['probability']:.2f}% | "
                    f"{selection['classification']}"
                )

        # --------------------------------------------
        # SALVAR NA MEMÓRIA
        # --------------------------------------------

        saved = register_prediction(
            memory,
            game,
            analysis,
            ticket
        )

        if saved:

            print()

            print(
                "✓ Previsão salva na "
                "memória do BET-AI."
            )

        else:

            print()

            print(
                "✓ Fixture já estava "
                "registrada na memória."
            )

        analyzed_count += 1

    # ------------------------------------------------
    # 5. SALVAR MEMÓRIA
    # ------------------------------------------------

    save_memory(
        memory
    )

    # ------------------------------------------------
    # 6. RELATÓRIO
    # ------------------------------------------------

    print_separator()

    print(
        "CICLO FINALIZADO"
    )

    print(
        f"Jogos analisados: "
        f"{analyzed_count}"
    )

    print_learning(
        memory
    )

    print_separator()

    print(
        "A memória será utilizada "
        "nas próximas análises."
    )


if __name__ == "__main__":
    main()
