import json

from match_analyzer import analyze_match


# ==========================================
# BET-AI V6
# ==========================================

MIN_PROBABILITY = 60.0
HIGH_PROBABILITY = 65.0


def classify(probability):
    """
    Classifica a probabilidade calculada pelo modelo.
    """

    if probability >= HIGH_PROBABILITY:
        return "🟢 ALTA"

    elif probability >= MIN_PROBABILITY:
        return "🟡 MÉDIA"

    else:
        return "🔴 BAIXA"


def get_candidates(probabilities):
    """
    Seleciona os mercados que atingiram
    a probabilidade mínima configurada.
    """

    candidates = []

    for market, values in probabilities.items():

        over = float(values.get("over", 0))
        under = float(values.get("under", 0))

        if over >= MIN_PROBABILITY:
            candidates.append({
                "market": market,
                "option": "Mais",
                "probability": over
            })

        if under >= MIN_PROBABILITY:
            candidates.append({
                "market": market,
                "option": "Menos",
                "probability": under
            })

    # Maior probabilidade primeiro
    candidates.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    return candidates


def print_statistics(stats):
    """
    Mostra as estatísticas do jogo.
    """

    print("\nESTATÍSTICAS")

    for market, values in stats.items():

        home = values.get("home", "-")
        away = values.get("away", "-")

        # Alguns mercados podem não possuir total.
        total = values.get("total")

        if total is None:
            print(
                f"{market}: "
                f"Casa {home} | "
                f"Fora {away}"
            )
        else:
            print(
                f"{market}: "
                f"Casa {home} | "
                f"Fora {away} | "
                f"Total {total}"
            )


def print_probabilities(probabilities):
    """
    Mostra todas as probabilidades.
    """

    print("\nPROBABILIDADES")

    for market, values in probabilities.items():

        over = float(values.get("over", 0))
        under = float(values.get("under", 0))

        print(
            f"{market}: "
            f"Mais = {over:.2f}% "
            f"[{classify(over)}] | "
            f"Menos = {under:.2f}% "
            f"[{classify(under)}]"
        )


def print_ticket(candidates):
    """
    Monta o resumo das principais seleções
    encontradas pelo modelo.
    """

    print("\n========== TALÃO BET-AI V6 ==========")

    if not candidates:
        print(
            "Nenhuma seleção atingiu "
            f"{MIN_PROBABILITY:.0f}% de probabilidade."
        )

        print(
            "\nO modelo não encontrou "
            "uma seleção dentro do filtro."
        )

        return

    # Limita o resumo às 3 maiores probabilidades
    top = candidates[:3]

    total = 0

    for index, item in enumerate(top, start=1):

        probability = item["probability"]

        print(
            f"{index}. "
            f"{item['market']} - "
            f"{item['option']} "
            f"({probability:.2f}%) "
            f"[{classify(probability)}]"
        )

        total += probability

    average = total / len(top)

    print("-------------------------------------")
    print(
        f"Probabilidade média: "
        f"{average:.2f}%"
    )

    print(
        "Filtro utilizado: "
        f"{MIN_PROBABILITY:.0f}%"
    )

    print(
        "Observação: estimativa do modelo, "
        "não garantia de resultado."
    )

    print("=====================================")


def analyze_game(game):
    """
    Analisa um jogo completo.
    """

    result = analyze_match(game)

    print("\n")
    print("=" * 50)

    print(
        f"JOGO: "
        f"{result['home']} x "
        f"{result['away']}"
    )

    print("=" * 50)

    stats = result.get("stats", {})
    probabilities = result.get("probabilities", {})

    print_statistics(stats)

    print_probabilities(probabilities)

    candidates = get_candidates(probabilities)

    print_ticket(candidates)


def main():

    print("\n========== BET-AI V6 ==========")

    print(
        f"Filtro mínimo: "
        f"{MIN_PROBABILITY:.0f}%"
    )

    print(
        f"Probabilidade alta: "
        f"{HIGH_PROBABILITY:.0f}%"
    )

    print("===============================\n")

    # Carrega os jogos
    with open(
        "data/matches.json",
        "r",
        encoding="utf-8"
    ) as file:

        matches = json.load(file)

    # Analisa cada jogo
    for game in matches:

        analyze_game(game)


if __name__ == "__main__":
    main()
