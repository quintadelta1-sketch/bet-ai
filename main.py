import json

from match_analyzer import analyze_match
from ticket import print_ticket


def classify(probability):
    if probability >= 65:
        return "🟢 ALTA"
    elif probability >= 55:
        return "🟡 MÉDIA"
    else:
        return "🔴 BAIXA"


def main():
    with open(
        "data/matches.json",
        "r",
        encoding="utf-8"
    ) as file:
        matches = json.load(file)

    print("\n========== BET-AI V5 ==========")

    for game in matches:
        result = analyze_match(game)

        print("\n" + "=" * 50)
        print(
            f"JOGO: {result['home']} "
            f"x {result['away']}"
        )
        print("=" * 50)

        print("\nESTATÍSTICAS")

        for market, values in result["stats"].items():
            home = values.get("home", 0)
            away = values.get("away", 0)
            total = values.get(
                "total",
                home + away
            )

            print(
                f"{market}: "
                f"Casa {home} | "
                f"Fora {away} | "
                f"Total {total}"
            )

        print("\nPROBABILIDADES")

        for market, values in result[
            "probabilities"
        ].items():

            over = float(
                values.get("over", 0)
            )

            under = float(
                values.get("under", 0)
            )

            print(
                f"{market}: "
                f"Mais = {over:.2f}% "
                f"[{classify(over)}] | "
                f"Menos = {under:.2f}% "
                f"[{classify(under)}]"
            )

        print_ticket(
            result["probabilities"]
        )

        print("\n")


if __name__ == "__main__":
    main()
