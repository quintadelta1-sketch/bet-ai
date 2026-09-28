def generate_ticket(probabilities, minimum_probability=65):
    selections = []

    for market, values in probabilities.items():
        over = float(values.get("over", 0))
        under = float(values.get("under", 0))

        if over >= minimum_probability:
            selections.append({
                "market": market,
                "selection": "Mais",
                "probability": over
            })

        if under >= minimum_probability:
            selections.append({
                "market": market,
                "selection": "Menos",
                "probability": under
            })

    selections.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    return selections[:3]


def print_ticket(probabilities):
    ticket = generate_ticket(probabilities)

    print("\n========== TALÃO BET-AI V5 ==========")

    if not ticket:
        print("Nenhum mercado atingiu o limite mínimo.")
        print("Nenhuma seleção foi adicionada.")
        return

    for number, item in enumerate(ticket, start=1):
        print(
            f"{number}. "
            f"{item['market']} - "
            f"{item['selection']} "
            f"({item['probability']:.2f}%)"
        )

    average = sum(
        item["probability"] for item in ticket
    ) / len(ticket)

    print("-------------------------------------")
    print(f"Probabilidade média: {average:.2f}%")
    print("Observação: estimativa do modelo, não garantia.")
    print("=====================================")
