# ============================================================
# BET-AI V10.1
# Modelo experimental de análise estatística de futebol
# ============================================================

FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 75.0
MAX_SELECOES = 3


# Pesos de cada mercado
WEIGHTS = {
    "goals": 0.20,
    "corners": 0.10,
    "shots": 0.20,
    "shots_on_target": 0.25,
    "tackles": 0.10,
    "cards": 0.05,
    "fouls": 0.10,
}


# Valores de referência usados pelo modelo experimental.
# Quanto maior o total em relação à referência,
# maior a estimativa para "Mais".
BASELINES = {
    "goals": 3.0,
    "corners": 10.0,
    "shots": 22.0,
    "shots_on_target": 9.0,
    "tackles": 28.0,
    "cards": 4.0,
    "fouls": 24.0,
}


def clamp(value, minimum=0.0, maximum=99.0):
    return max(minimum, min(maximum, value))


def classification(probability):
    if probability >= PROBABILIDADE_ALTA:
        return "ALTA"

    if probability >= FILTRO_MINIMO:
        return "MEDIA"

    return "BAIXA"


def calculate_over_probability(market, home_value, away_value):
    total = home_value + away_value
    baseline = BASELINES[market]

    if baseline <= 0:
        return 50.0

    ratio = total / baseline

    # Modelo experimental:
    # 50% representa equilíbrio.
    # O excesso estatístico acima da referência
    # aumenta a estimativa gradualmente.
    probability = 50.0 + (ratio * 25.0)

    return clamp(probability)


def calculate_under_probability(over_probability):
    return clamp(100.0 - over_probability)


def calculate_score(probability, weight):
    return round(probability * weight, 2)


def build_markets(game):
    markets = []

    for market, weight in WEIGHTS.items():

        home_value = float(game[market]["home"])
        away_value = float(game[market]["away"])

        over = calculate_over_probability(
            market,
            home_value,
            away_value
        )

        under = calculate_under_probability(over)

        # Mercado MAIS
        if over >= FILTRO_MINIMO:
            markets.append({
                "market": market,
                "side": "Mais",
                "probability": round(over, 2),
                "opposite": round(under, 2),
                "score": calculate_score(over, weight),
                "classification": classification(over),
            })

        # Mercado MENOS
        if under >= FILTRO_MINIMO:
            markets.append({
                "market": market,
                "side": "Menos",
                "probability": round(under, 2),
                "opposite": round(over, 2),
                "score": calculate_score(under, weight),
                "classification": classification(under),
            })

    return markets


def select_markets(markets):

    ordered = sorted(
        markets,
        key=lambda item: (
            item["score"],
            item["probability"]
        ),
        reverse=True
    )

    selected = []
    used_markets = set()

    for item in ordered:

        market_name = item["market"]

        # Não repetir o mesmo mercado
        if market_name in used_markets:
            continue

        selected.append(item)
        used_markets.add(market_name)

        if len(selected) >= MAX_SELECOES:
            break

    return selected


def print_statistics(game):

    print("\nESTATÍSTICAS")

    for market in WEIGHTS:

        home = game[market]["home"]
        away = game[market]["away"]

        print(
            f"{market}: "
            f"Casa {home} | "
            f"Fora {away}"
        )


def print_probabilities(markets):

    print("\nPROBABILIDADES")

    for market in WEIGHTS:

        candidates = [
            item
            for item in markets
            if item["market"] == market
        ]

        if not candidates:
            continue

        best = max(
            candidates,
            key=lambda item: item["probability"]
        )

        print(
            f"{market}: "
            f"{best['side']} = "
            f"{best['probability']:.2f}% "
            f"[{best['classification']}]"
        )


def print_ticket(selected):

    print(
        "\n========== TALÃO BET-AI V10.1 =========="
    )

    if not selected:

        print(
            "Nenhum mercado atingiu "
            "o filtro mínimo."
        )

        return 0.0

    for number, item in enumerate(
        selected,
        start=1
    ):

        print(
            f"{number}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )

    average_probability = (
        sum(
            item["probability"]
            for item in selected
        )
        / len(selected)
    )

    print("-" * 48)

    print(
        f"Probabilidade média: "
        f"{average_probability:.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )

    return average_probability


def print_discarded(markets, selected):

    print(
        "\n========== MERCADOS DESCARTADOS =========="
    )

    selected_keys = {
        (
            item["market"],
            item["side"]
        )
        for item in selected
    }

    discarded = [
        item
        for item in markets
        if (
            item["market"],
            item["side"]
        )
        not in selected_keys
    ]

    discarded.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    if not discarded:

        print(
            "Nenhum mercado descartado."
        )

        return

    for item in discarded:

        print(
            f"- {item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )


def analyze_game(game):

    markets = build_markets(game)

    selected = select_markets(markets)

    print("\n" + "=" * 48)

    print(
        f"JOGO: "
        f"{game['home_team']} x "
        f"{game['away_team']}"
    )

    print("=" * 48)

    print_statistics(game)

    print_probabilities(markets)

    average_probability = print_ticket(
        selected
    )

    print_discarded(
        markets,
        selected
    )

    print(
        "\nObservação: estimativa "
        "experimental do modelo, "
        "não garantia de resultado."
    )

    print("=" * 48)

    return {
        "game": (
            f"{game['home_team']} x "
            f"{game['away_team']}"
        ),
        "selected": selected,
        "average_probability": (
            round(average_probability, 2)
        ),
    }


def main():

    games = [

        {
            "home_team": "Flamengo",
            "away_team": "Palmeiras",

            "goals": {
                "home": 1.8,
                "away": 1.4
            },

            "corners": {
                "home": 6.2,
                "away": 4.8
            },

            "shots": {
                "home": 14.5,
                "away": 11.2
            },

            "shots_on_target": {
                "home": 5.8,
                "away": 4.3
            },

            "tackles": {
                "home": 15.0,
                "away": 16.2
            },

            "cards": {
                "home": 2.1,
                "away": 2.5
            },

            "fouls": {
                "home": 12.4,
                "away": 13.1
            },
        },

        {
            "home_team": "Barcelona",
            "away_team": "Real Madrid",

            "goals": {
                "home": 2.1,
                "away": 1.7
            },

            "corners": {
                "home": 6.5,
                "away": 5.1
            },

            "shots": {
                "home": 16.2,
                "away": 12.8
            },

            "shots_on_target": {
                "home": 6.4,
                "away": 5.0
            },

            "tackles": {
                "home": 13.8,
                "away": 15.1
            },

            "cards": {
                "home": 1.8,
                "away": 2.3
            },

            "fouls": {
                "home": 10.8,
                "away": 12.7
            },
        },
    ]

    print(
        "\n========== BET-AI V10.1 =========="
    )

    print(
        f"Filtro mínimo: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Probabilidade alta: "
        f"{PROBABILIDADE_ALTA:.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )

    print("=" * 48)

    results = []

    for game in games:

        result = analyze_game(game)

        results.append(result)

    print(
        "\n" + "=" * 48
    )

    print(
        "BET-AI V10.1 FINALIZADO"
    )

    print(
        "=" * 48
    )


if __name__ == "__main__":
    main()
