from config import (
    MAX_GAMES,
    CANDIDATE_GAMES,
    MIN_PROBABILITY,
    MAX_SELECTIONS,
)

from data_provider import (
    FootballDataProvider,
)

from analyzer import analyze_game
from ticket import build_ticket

from memory import (
    load_memory,
    save_memory,
    register_prediction,
    update_finished_fixtures,
    get_learning_stats,
)


# ============================================================
# BET-AI
# MAIN
# ============================================================


def get_fixture_id(game):
    """
    Obtém o ID da partida independentemente
    da estrutura retornada pela API.
    """

    # Estrutura já normalizada
    if game.get("fixture_id") is not None:
        return int(game["fixture_id"])

    # Estrutura simples
    if game.get("id") is not None:
        return int(game["id"])

    # Estrutura da API-Football
    fixture = game.get("fixture")

    if isinstance(fixture, dict):
        if fixture.get("id") is not None:
            return int(fixture["id"])

    return None


def get_team_name(game, side):
    """
    Obtém nome do time de forma segura.
    """

    if side in game:
        value = game.get(side)

        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            return value.get("name", "Desconhecido")

    teams = game.get("teams", {})

    if isinstance(teams, dict):
        team = teams.get(side)

        if isinstance(team, dict):
            return team.get("name", "Desconhecido")

    return "Desconhecido"


def normalize_game(game):
    """
    Normaliza o jogo para o padrão interno do BET-AI.
    """

    fixture_id = get_fixture_id(game)

    if fixture_id is None:
        return None

    home = get_team_name(game, "home")
    away = get_team_name(game, "away")

    normalized = dict(game)

    normalized["fixture_id"] = fixture_id
    normalized["home"] = home
    normalized["away"] = away

    return normalized


def safe_prediction(provider, fixture_id):
    """
    Busca previsão da API com tratamento de erro.
    """

    try:
        return provider.get_prediction(fixture_id)

    except Exception as error:
        print(
            f"ERRO NA PREVISÃO {fixture_id}: {error}"
        )
        return None


def safe_odds(provider, fixture_id):
    """
    Busca odds da partida.

    Se não houver odds, o BET-AI continua funcionando.
    """

    try:
        return provider.get_odds(fixture_id)

    except Exception as error:
        print(
            f"Aviso: não foi possível obter odds "
            f"da partida {fixture_id}: {error}"
        )

        return None


def main():

    print()
    print("=" * 50)
    print("BET-AI")
    print("SISTEMA DE ANÁLISE E APRENDIZADO")
    print("=" * 50)
    print()

    # --------------------------------------------------------
    # 1. MEMÓRIA
    # --------------------------------------------------------

    print("Carregando memória...")

    memory = load_memory()

    print(
        f"Memória carregada: "
        f"{len(memory.get('predictions', []))} previsões."
    )

    print()

    # --------------------------------------------------------
    # 2. ATUALIZAR RESULTADOS ANTERIORES
    # --------------------------------------------------------

    print("=" * 50)
    print("ATUALIZANDO RESULTADOS")
    print("=" * 50)

    try:

        update_finished_fixtures()

        # Recarrega a memória depois da atualização
        memory = load_memory()

    except Exception as error:

        print(
            f"Aviso: não foi possível atualizar "
            f"todos os resultados: {error}"
        )

    print()

    # --------------------------------------------------------
    # 3. PROVIDER
    # --------------------------------------------------------

    provider = FootballDataProvider()

    # --------------------------------------------------------
    # 4. BUSCAR JOGOS
    # --------------------------------------------------------

    print("=" * 50)
    print("BUSCANDO JOGOS")
    print("=" * 50)

    try:

        games = provider.get_upcoming_games()

    except Exception as error:

        print()
        print("ERRO AO BUSCAR JOGOS:")
        print(error)
        print()

        save_memory(memory)
        return

    if not games:

        print("Nenhum jogo encontrado.")

        save_memory(memory)

        return

    print(
        f"Jogos encontrados pela API: {len(games)}"
    )

    print()

    # --------------------------------------------------------
    # 5. NORMALIZAR JOGOS
    # --------------------------------------------------------

    normalized_games = []

    for game in games:

        normalized = normalize_game(game)

        if normalized is None:

            print(
                "Aviso: jogo ignorado porque "
                "não possui fixture ID."
            )

            continue

        normalized_games.append(normalized)

    # Remove partidas duplicadas
    unique_games = []
    seen_ids = set()

    for game in normalized_games:

        fixture_id = game["fixture_id"]

        if fixture_id in seen_ids:
            continue

        seen_ids.add(fixture_id)
        unique_games.append(game)

    games = unique_games

    print(
        f"Jogos válidos: {len(games)}"
    )

    print()

    # --------------------------------------------------------
    # 6. LIMITAR CANDIDATOS
    # --------------------------------------------------------

    candidates = games[:CANDIDATE_GAMES]

    print(
        f"Candidatos para análise: {len(candidates)}"
    )

    print()

    # --------------------------------------------------------
    # 7. ANALISAR
    # --------------------------------------------------------

    analyses = []

    for game in candidates:

        fixture_id = game["fixture_id"]

        home = game.get(
            "home",
            "Casa"
        )

        away = game.get(
            "away",
            "Fora"
        )

        print("=" * 50)

        print(
            f"Testando previsão: "
            f"{home} x {away}"
        )

        print(
            f"Fixture ID: {fixture_id}"
        )

        print()

        # ----------------------------------------------
        # PREVISÃO
        # ----------------------------------------------

        prediction = safe_prediction(
            provider,
            fixture_id
        )

        if not prediction:

            print(
                "Sem previsão disponível."
            )

            continue

        # ----------------------------------------------
        # ODDS
        # ----------------------------------------------

        odds = safe_odds(
            provider,
            fixture_id
        )

        # ----------------------------------------------
        # ANÁLISE
        # ----------------------------------------------

        try:

            analysis = analyze_game(
                game=game,
                prediction=prediction,
                odds=odds,
                memory=memory,
            )

        except TypeError:

            # Compatibilidade com versões
            # diferentes do analyzer.py
            try:

                analysis = analyze_game(
                    game,
                    prediction,
                    odds,
                    memory,
                )

            except Exception as error:

                print(
                    f"Erro na análise: {error}"
                )

                continue

        except Exception as error:

            print(
                f"Erro na análise: {error}"
            )

            continue

        if not analysis:

            print(
                "Análise vazia."
            )

            continue

        # ------------------------------------------------
        # GARANTIR IDENTIFICAÇÃO
        # ------------------------------------------------

        if isinstance(analysis, dict):

            analysis["fixture_id"] = fixture_id
            analysis["home"] = home
            analysis["away"] = away

        analyses.append(analysis)

        print(
            "Análise concluída."
        )

        print()

        # ------------------------------------------------
        # PARAR QUANDO TIVER JOGOS SUFICIENTES
        # ------------------------------------------------

        if len(analyses) >= MAX_GAMES:
            break

    # --------------------------------------------------------
    # 8. RESULTADO DAS ANÁLISES
    # --------------------------------------------------------

    print()
    print("=" * 50)
    print("RESULTADO DAS ANÁLISES")
    print("=" * 50)

    print(
        f"Análises concluídas: {len(analyses)}"
    )

    print()

    if not analyses:

        print(
            "Nenhuma análise válida foi produzida."
        )

        save_memory(memory)

        return

    # --------------------------------------------------------
    # 9. MONTAR BILHETE
    # --------------------------------------------------------

    print("=" * 50)
    print("MONTANDO SELEÇÕES")
    print("=" * 50)

    try:

        ticket = build_ticket(
            analyses,
            min_probability=MIN_PROBABILITY,
            max_selections=MAX_SELECTIONS,
        )

    except TypeError:

        try:

            ticket = build_ticket(
                analyses
            )

        except Exception as error:

            print(
                f"Erro ao montar bilhete: {error}"
            )

            ticket = []

    except Exception as error:

        print(
            f"Erro ao montar bilhete: {error}"
        )

        ticket = []

    # --------------------------------------------------------
    # 10. MOSTRAR ANÁLISES
    # --------------------------------------------------------

    print()

    for analysis in analyses:

        fixture_id = analysis.get(
            "fixture_id"
        )

        home = analysis.get(
            "home",
            "Casa"
        )

        away = analysis.get(
            "away",
            "Fora"
        )

        print("-" * 50)

        print(
            f"{home} x {away}"
        )

        print(
            f"Fixture: {fixture_id}"
        )

        # Probabilidades
        probabilities = analysis.get(
            "probabilities",
            {}
        )

        if probabilities:

            print(
                "Probabilidades:"
            )

            for market, value in probabilities.items():

                if isinstance(value, (int, float)):

                    print(
                        f"  {market}: "
                        f"{value:.1f}%"
                    )

        # Seleções
        selections = analysis.get(
            "selections",
            []
        )

        if selections:

            print(
                "Seleções:"
            )

            for selection in selections:

                if isinstance(selection, dict):

                    market = selection.get(
                        "market",
                        "?"
                    )

                    probability = selection.get(
                        "probability"
                    )

                    if probability is not None:

                        print(
                            f"  {market}: "
                            f"{probability:.1f}%"
                        )

                    else:

                        print(
                            f"  {market}"
                        )

                else:

                    print(
                        f"  {selection}"
                    )

    # --------------------------------------------------------
    # 11. MOSTRAR BILHETE
    # --------------------------------------------------------

    print()
    print("=" * 50)
    print("BET-AI — BILHETE")
    print("=" * 50)

    if not ticket:

        print(
            "Nenhuma seleção atingiu "
            "os critérios mínimos."
        )

    else:

        for index, selection in enumerate(
            ticket,
            start=1
        ):

            print(
                f"{index}. {selection}"
            )

    # --------------------------------------------------------
    # 12. SALVAR PREVISÕES NA MEMÓRIA
    # --------------------------------------------------------

    print()
    print("=" * 50)
    print("SALVANDO PREVISÕES")
    print("=" * 50)

    for analysis in analyses:

        fixture_id = analysis.get(
            "fixture_id"
        )

        if fixture_id is None:
            continue

        try:

            register_prediction(
                memory=memory,
                fixture_id=fixture_id,
                game=analysis,
                prediction=analysis,
                selected_ticket=(
                    ticket if ticket else []
                ),
            )

            print(
                f"Previsão salva: {fixture_id}"
            )

        except TypeError:

            # Compatibilidade caso a função
            # tenha assinatura diferente
            try:

                register_prediction(
                    memory,
                    fixture_id,
                    analysis,
                    ticket,
                )

                print(
                    f"Previsão salva: {fixture_id}"
                )

            except Exception as error:

                print(
                    f"Erro salvando "
                    f"{fixture_id}: {error}"
                )

        except Exception as error:

            print(
                f"Erro salvando "
                f"{fixture_id}: {error}"
            )

    # --------------------------------------------------------
    # 13. SALVAR MEMÓRIA
    # --------------------------------------------------------

    try:

        save_memory(memory)

        print()
        print(
            "Memória salva com sucesso."
        )

    except Exception as error:

        print()
        print(
            f"Erro ao salvar memória: {error}"
        )

    # --------------------------------------------------------
    # 14. ESTATÍSTICAS DE APRENDIZADO
    # --------------------------------------------------------

    print()
    print("=" * 50)
    print("APRENDIZADO DO BET-AI")
    print("=" * 50)

    try:

        stats = get_learning_stats(
            memory
        )

        if not stats:

            print(
                "Ainda não existem dados "
                "suficientes para aprendizado."
            )

        else:

            for market, data in stats.items():

                if not isinstance(data, dict):
                    continue

                total = data.get(
                    "total",
                    data.get("samples", 0)
                )

                hits = data.get(
                    "hits",
                    data.get("correct", 0)
                )

                accuracy = data.get(
                    "accuracy",
                    0
                )

                print(
                    f"{market}: "
                    f"{hits}/{total} "
                    f"({accuracy:.1f}%)"
                )

    except Exception as error:

        print(
            f"Aviso: estatísticas "
            f"indisponíveis: {error}"
        )

    print()
    print("=" * 50)
    print("BET-AI FINALIZADO")
    print("=" * 50)
    print()


if __name__ == "__main__":
    main()
