# BET-AI V10
# Modelo experimental de análise estatística de futebol.
# As probabilidades são estimativas do modelo e não garantias.

FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 75.0
MAX_SELECOES = 3

WEIGHTS = {
    "goals": 0.20,
    "corners": 0.10,
    "shots": 0.20,
    "shots_on_target": 0.25,
    "tackles": 0.10,
    "cards": 0.05,
    "fouls": 0.10,
}


def clamp(value, minimum=0.0, maximum=99.0):
    return max(minimum, min(maximum, value))


def classification(probability):
    if probability >= PROBABILIDADE_ALTA:
        return "ALTA"
    if probability >= FILTRO_MINIMO:
        return "MEDIA"
    return "BAIXA"


def probability_for_over(home, away):
    ratio = home / (home + away) if (home + away) else 0.5
    probability = 50.0 + (ratio - 0.5) * 70.0
    return clamp(probability)


def probability_for_under(over_probability):
    return clamp(100.0 - over_probability)


def calculate_score(probability, weight):
    return round(probability * weight, 2)


def build_markets(game):
    markets = []

    for market, weight in WEIGHTS.items():
        home_value = float(game[market]["home"])
        away_value = float(game[market]["away"])

        over = probability_for_over(home_value, away_value)
        under = probability_for_under(over)

        if over >= FILTRO_MINIMO:
            markets.append({
                "market": market,
                "side": "Mais",
                "probability": round(over, 2),
                "opposite": round(under, 2),
                "score": calculate_score(over, weight),
                "classification": classification(over),
            })

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
        key=lambda item: (item["score"], item["probability"]),
        reverse=True,
    )

    selected = []
    used_markets = set()

    for item in ordered:
        market_name = item["market"]

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
        print(f"{market}: Casa {home} | Fora {away}")


def analyze_game(game):
    markets = build_markets(game)
    selected = select_markets(markets)

    print("\n" + "=" * 48)
    print(f"JOGO: {game['home_team']} x {game['away_team']}")
    print("=" * 48)

    print_statistics(game)

    print("\nPROBABILIDADES")

    for market in WEIGHTS:
        candidates = [
            m for m in markets
            if m["market"] == market
        ]

        if not candidates:
            continue

        best = max(
            candidates,
            key=lambda item: item["probability"]
        )

        print(
            f"{market}: {best['side']} = "
            f"{best['probability']:.2f}% "
            f"[{best['classification']}]"
        )

    print("\n========== TALÃO BET-AI V10 ==========")

    if not selected:
        print("Nenhum mercado atingiu o filtro mínimo.")
        average_probability = 0.0

    else:
        for number, item in enumerate(selected, start=1):
            print(
                f"{number}. {item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%) "
                f"[{item['classification']}]"
            )

        average_probability = sum(
            item["probability"]
            for item in selected
        ) / len(selected)

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

    print("\n========== MERCADOS DESCARTADOS ==========")

    selected_keys = {
        (item["market"], item["side"])
        for item in selected
    }

    discarded = [
        item for item in markets
        if (item["market"], item["side"])
        not in selected_keys
    ]

    discarded.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    if discarded:
        for item in discarded:
            print(
                f"- {item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%)"
            )
    else:
        print("Nenhum mercado descartado.")

    print(
        "\nObservação: estimativa do modelo, "
        "não garantia de resultado."
    )

    print("=" * 48)

    return selected


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

    print("\n========== BET-AI V10 ==========")

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

    for game in games:
        analyze_game(game)

    print("\n" + "=" * 48)
    print("BET-AI V10 FINALIZADO")
    print("=" * 48)


if __name__ == "__main__":
    main()
