FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 65.0


def classify(probability):
    if probability >= PROBABILIDADE_ALTA:
        return "ALTA"
    if probability >= FILTRO_MINIMO:
        return "MEDIA"
    return "BAIXA"


def calculate_score(probability, edge):
    return round((probability * 0.7) + (edge * 0.3), 2)


def analyze_market(market, over, under):
    markets = []

    if over >= FILTRO_MINIMO:
        markets.append({
            "market": market,
            "side": "Mais",
            "probability": over,
            "opposite": under,
            "edge": round(abs(over - under), 2),
            "score": calculate_score(over, abs(over - under)),
            "classification": classify(over),
        })

    if under >= FILTRO_MINIMO:
        markets.append({
            "market": market,
            "side": "Menos",
            "probability": under,
            "opposite": over,
            "edge": round(abs(under - over), 2),
            "score": calculate_score(under, abs(under - over)),
            "classification": classify(under),
        })

    return markets


def build_markets(stats):

    formulas = {
        "goals": lambda s: min(
            95.0,
            max(
                5.0,
                40.0
                + (s["goals_home"] + s["goals_away"]) * 7.5
            ),
        ),

        "corners": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["corners_home"] + s["corners_away"]) * 2.08
            ),
        ),

        "shots": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["shots_home"] + s["shots_away"]) * 1.08
            ),
        ),

        "shots_on_target": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["sot_home"] + s["sot_away"]) * 3.2
            ),
        ),

        "tackles": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["tackles_home"] + s["tackles_away"]) * 0.70
            ),
        ),

        "cards": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["cards_home"] + s["cards_away"]) * 2.4
            ),
        ),

        "fouls": lambda s: min(
            95.0,
            max(
                5.0,
                35.0
                + (s["fouls_home"] + s["fouls_away"]) * 0.68
            ),
        ),
    }

    markets = []

    for market, formula in formulas.items():

        over = round(formula(stats), 2)
        under = round(100.0 - over, 2)

        markets.extend(
            analyze_market(
                market,
                over,
                under
            )
        )

    return markets


def select_markets(markets, limit=3):

    markets = sorted(
        markets,
        key=lambda x: x["score"],
        reverse=True
    )

    selected = []
    used_markets = set()

    for item in markets:

        if item["market"] in used_markets:
            continue

        selected.append(item)

        used_markets.add(
            item["market"]
        )

        if len(selected) >= limit:
            break

    return selected


def print_game(game):

    print("\n" + "=" * 48)

    print(
        f"JOGO: {game['home']} x {game['away']}"
    )

    print("=" * 48)

    s = game["stats"]

    print("\nESTATÍSTICAS")

    print(
        f"goals: Casa {s['goals_home']} | "
        f"For a {s['goals_away']}"
    )

    print(
        f"corners: Casa {s['corners_home']} | "
        f"Fora {s['corners_away']}"
    )

    print(
        f"shots: Casa {s['shots_home']} | "
        f"Fora {s['shots_away']}"
    )

    print(
        f"shots_on_target: Casa {s['sot_home']} | "
        f"Fora {s['sot_away']}"
    )

    print(
        f"tackles: Casa {s['tackles_home']} | "
        f"Fora {s['tackles_away']}"
    )

    print(
        f"cards: Casa {s['cards_home']} | "
        f"Fora {s['cards_away']}"
    )

    print(
        f"fouls: Casa {s['fouls_home']} | "
        f"Fora {s['fouls_away']}"
    )

    markets = build_markets(s)

    print("\nPROBABILIDADES")

    for market in markets:

        if market["classification"] == "ALTA":
            emoji = "🟢"
        elif market["classification"] == "MEDIA":
            emoji = "🟡"
        else:
            emoji = "🔴"

        print(
            f"{market['market']}: "
            f"{market['side']} = "
            f"{market['probability']:.2f}% "
            f"[{emoji} {market['classification']}]"
        )

    selected = select_markets(
        markets,
        limit=3
    )

    print(
        "\n========== TALÃO BET-AI V8 =========="
    )

    if not selected:

        print(
            "Nenhum mercado atingiu "
            "o filtro mínimo."
        )

        print(
            f"Filtro utilizado: "
            f"{FILTRO_MINIMO:.0f}%"
        )

        return

    total = 0.0

    for number, item in enumerate(
        selected,
        start=1
    ):

        if item["classification"] == "ALTA":
            emoji = "🟢"
        else:
            emoji = "🟡"

        print(
            f"{number}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{emoji} "
            f"{item['classification']}]"
        )

        total += item["probability"]

    average = (
        total / len(selected)
    )

    print(
        "-" * 48
    )

    print(
        f"Probabilidade média: "
        f"{average:.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        "Observação: estimativa do "
        "modelo, não garantia de resultado."
    )

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
        ) not in selected_keys
    ]

    if discarded:

        for item in discarded:

            print(
                f"- {item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%) "
                f"abaixo do filtro ou não selecionado"
            )

    else:

        print(
            "- Nenhum mercado descartado."
        )


def main():

    print(
        "============ BET-AI V8 ============"
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
        "===================================="
    )

    games = [

        {
            "home": "Flamengo",
            "away": "Palmeiras",

            "stats": {

                "goals_home": 1.8,
                "goals_away": 1.4,

                "corners_home": 6.2,
                "corners_away": 4.8,

                "shots_home": 14.5,
                "shots_away": 11.2,

                "sot_home": 5.8,
                "sot_away": 4.3,

                "tackles_home": 15.0,
                "tackles_away": 16.2,

                "cards_home": 2.1,
                "cards_away": 2.5,

                "fouls_home": 12.4,
                "fouls_away": 13.1,
            },
        },

        {
            "home": "Barcelona",
            "away": "Real Madrid",

            "stats": {

                "goals_home": 2.1,
                "goals_away": 1.7,

                "corners_home": 6.5,
                "corners_away": 5.1,

                "shots_home": 16.2,
                "shots_away": 12.8,

                "sot_home": 6.4,
                "sot_away": 5.0,

                "tackles_home": 13.8,
                "tackles_away": 15.1,

                "cards_home": 1.8,
                "cards_away": 2.3,

                "fouls_home": 10.8,
                "fouls_away": 12.7,
            },
        },
    ]

    for game in games:

        print_game(game)


if __name__ == "__main__":

    main()
