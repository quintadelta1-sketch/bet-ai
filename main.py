import json

from match_analyzer import analyze_match


FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 65.0
MAX_MERCADOS = 3


def classify(probability):
    if probability >= PROBABILIDADE_ALTA:
        return "🟢 ALTA"
    elif probability >= FILTRO_MINIMO:
        return "🟡 MÉDIA"
    else:
        return "🔴 BAIXA"


def calculate_score(probability, opposite_probability):
    """
    Pontuação experimental do modelo.

    A pontuação considera:
    - probabilidade principal
    - distância em relação à probabilidade oposta

    Não representa garantia de resultado.
    """

    edge = abs(probability - opposite_probability)

    score = (
        probability * 0.75
        + edge * 0.25
    )

    return round(score, 2)


def get_markets(result):

    markets = []

    for market, values in result["probabilities"].items():

        over = float(values["over"])
        under = float(values["under"])

        # Mercado MAIS
        if over >= FILTRO_MINIMO:

            markets.append({
                "market": market,
                "side": "Mais",
                "probability": over,
                "opposite": under,
                "edge": round(abs(over - under), 2),
                "score": calculate_score(over, under),
                "classification": classify(over)
            })

        # Mercado MENOS
        if under >= FILTRO_MINIMO:

            markets.append({
                "market": market,
                "side": "Menos",
                "probability": under,
                "opposite": over,
                "edge": round(abs(under - over), 2),
                "score": calculate_score(under, over),
                "classification": classify(under)
            )

    return markets


def select_markets(markets):

    # Ordena pela pontuação do modelo
    markets = sorted(
        markets,
        key=lambda x: x["score"],
        reverse=True
    )

    selected = []
    used_markets = set()

    for item in markets:

        # Evita repetir o mesmo mercado
        if item["market"] in used_markets:
            continue

        selected.append(item)
        used_markets.add(item["market"])

        if len(selected) >= MAX_MERCADOS:
            break

    return selected


def print_ticket(selected):

    print("\n========== TALÃO BET-AI V7.1 ==========")

    if not selected:

        print("Nenhum mercado atingiu o filtro mínimo.")
        return

    total_probability = 0

    for index, item in enumerate(selected, start=1):

        print(
            f"{index}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )

        print(
            f"   Pontuação: {item['score']:.2f} "
            f"| Diferença: {item['edge']:.2f}%"
        )

        total_probability += item["probability"]

    average = total_probability / len(selected)

    print("----------------------------------------")
    print(f"Probabilidade média: {average:.2f}%")
    print(f"Filtro mínimo: {FILTRO_MINIMO:.0f}%")
    print(f"Probabilidade alta: {PROBABILIDADE_ALTA:.0f}%")

    print(
        "Observação: estimativa experimental "
        "do modelo, não garantia de resultado."
    )

    print("========================================")


def print_discarded(all_markets, selected):

    selected_names = {
        (item["market"], item["side"])
        for item in selected
    }

    discarded = []

    for item in all_markets:

        key = (item["market"], item["side"])

        if key not in selected_names:
            discarded.append(item)

    print("\n========== MERCADOS NÃO SELECIONADOS ==========")

    if not discarded:

        print("Nenhum mercado adicional.")

        return

    for item in discarded:

        print(
            f"- {item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"| Score {item['score']:.2f}"
        )

    print("===============================================")


def print_statistics(result):

    print("\nESTATÍSTICAS")

    for market, values in result["stats"].items():

        home = values.get("home")
        away = values.get("away")

        if home is not None and away is not None:

            print(
                f"{market}: "
                f"Casa {home} | "
                f"Fora {away}"
            )


def print_probabilities(result):

    print("\nPROBABILIDADES")

    for market, values in result["probabilities"].items():

        over = float(values["over"])
        under = float(values["under"])

        print(
            f"{market}: "
            f"Mais = {over:.2f}% "
            f"[{classify(over)}] | "
            f"Menos = {under:.2f}% "
            f"[{classify(under)}]"
        )


def main():

    with open(
        "data/matches.json",
        "r",
        encoding="utf-8"
    ) as file:

        matches = json.load(file)

    print("\n========== BET-AI V7.1 ==========")
    print(f"Filtro mínimo: {FILTRO_MINIMO:.0f}%")
    print(f"Probabilidade alta: {PROBABILIDADE_ALTA:.0f}%")
    print(f"Máximo de mercados: {MAX_MERCADOS}")
    print("=================================\n")

    for game in matches:

        result = analyze_match(game)

        print("\n" + "=" * 45)

        print(
            f"JOGO: "
            f"{result['home']} x "
            f"{result['away']}"
        )

        print("=" * 45)

        print_statistics(result)

        print_probabilities(result)

        all_markets = get_markets(result)

        selected = select_markets(all_markets)

        print_ticket(selected)

        print_discarded(all_markets, selected)


if __name__ == "__main__":
    main()
