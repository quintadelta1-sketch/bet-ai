import json

from match_analyzer import analyze_match


FILTRO_MODERADO = 60
FILTRO_CONSERVADOR = 65


def classify(probability):
    if probability >= FILTRO_CONSERVADOR:
        return "🟢 ALTA"
    elif probability >= FILTRO_MODERADO:
        return "🟡 MÉDIA"
    else:
        return "🔴 BAIXA"


def get_markets(result):
    markets = []

    for market, values in result["probabilities"].items():

        over = float(values["over"])
        under = float(values["under"])

        markets.append({
            "market": market,
            "side": "Mais",
            "probability": over,
            "classification": classify(over)
        })

        markets.append({
            "market": market,
            "side": "Menos",
            "probability": under,
            "classification": classify(under)
        })

    return markets


def create_ticket(result):
    markets = get_markets(result)

    # Apenas mercados que atingem o filtro mínimo
    approved = [
        market for market in markets
        if market["probability"] >= FILTRO_MODERADO
    ]

    # Ordena da maior para a menor probabilidade
    approved.sort(
        key=lambda x: x["probability"],
        reverse=True
    )

    # Seleciona no máximo 3 mercados
    ticket = approved[:3]

    return ticket, markets


def print_ticket(ticket):

    print("\n========== TALÃO BET-AI V7 ==========")

    if not ticket:
        print("Nenhum mercado atingiu o filtro mínimo.")
        return

    total = 0

    for index, item in enumerate(ticket, start=1):

        print(
            f"{index}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )

        total += item["probability"]

    average = total / len(ticket)

    print("--------------------------------------")
    print(f"Probabilidade média: {average:.2f}%")
    print(f"Filtro utilizado: {FILTRO_MODERADO}%")
    print(
        "Observação: estimativa do modelo, "
        "não garantia de resultado."
    )
    print("======================================")


def print_rejected(markets):

    rejected = [
        market for market in markets
        if market["probability"] < FILTRO_MODERADO
    ]

    print("\n========== MERCADOS DESCARTADOS ==========")

    if not rejected:
        print("Nenhum mercado foi descartado.")
        return

    for item in rejected:

        print(
            f"- {item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"abaixo de {FILTRO_MODERADO}%"
        )

    print("===========================================")


def main():

    with open(
        "data/matches.json",
        "r",
        encoding="utf-8"
    ) as file:

        matches = json.load(file)

    print("\n========== BET-AI V7 ==========")
    print(f"Filtro mínimo: {FILTRO_MODERADO}%")
    print(f"Probabilidade alta: {FILTRO_CONSERVADOR}%")
    print("===============================\n")

    for game in matches:

        result = analyze_match(game)

        print("\n" + "=" * 45)
        print(
            f"JOGO: "
            f"{result['home']} x "
            f"{result['away']}"
        )
        print("=" * 45)

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

        ticket, markets = create_ticket(result)

        print_ticket(ticket)

        print_rejected(markets)


if __name__ == "__main__":
    main()
