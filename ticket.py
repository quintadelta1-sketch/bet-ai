from config import MIN_PROBABILITY


def generate_ticket(
    analysis,
    maximum_selections=3
):

    markets = analysis.get(
        "markets",
        []
    )

    eligible = []

    for market in markets:

        probability = market.get(
            "probability",
            0
        )

        classification = market.get(
            "classification",
            "BAIXA"
        )

        # ----------------------------------------------------
        # FILTRO
        # ----------------------------------------------------

        if probability < MIN_PROBABILITY:
            continue

        if classification == "BAIXA":
            continue

        eligible.append(
            market
        )

    # --------------------------------------------------------
    # MELHORES PRIMEIRO
    # --------------------------------------------------------

    eligible.sort(
        key=lambda item:
            item["probability"],
        reverse=True
    )

    # --------------------------------------------------------
    # LIMITE
    # --------------------------------------------------------

    return eligible[
        :maximum_selections
    ]


def print_ticket(
    analysis,
    ticket
):

    print()
    print("=" * 60)
    print("BET-AI - SELEÇÕES")
    print("=" * 60)

    print(
        f"{analysis['home']} x "
        f"{analysis['away']}"
    )

    print()

    if not ticket:

        print(
            "Nenhuma seleção atingiu "
            "o limite mínimo."
        )

        print("=" * 60)

        return

    for index, selection in enumerate(
        ticket,
        start=1
    ):

        print(
            f"{index}. "
            f"{selection['market']}"
        )

        print(
            f"   Probabilidade: "
            f"{selection['probability']}%"
        )

        print(
            f"   Classificação: "
            f"{selection['classification']}"
        )

        print()

    print("=" * 60)
