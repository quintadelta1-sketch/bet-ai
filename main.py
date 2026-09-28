import json

from match_analyzer import analyze_match


def classify(probability):
    if probability >= 65:
        return "🟢 ALTA"
    elif probability >= 55:
        return "🟡 MÉDIA"
    else:
        return "🔴 BAIXA"


def main():
    with open("data/matches.json", "r", encoding="utf-8") as file:
        matches = json.load(file)

    print("\n========== BET-AI V4 ==========")

    for game in matches:
        result = analyze_match(game)

        print("\n" + "=" * 50)
        print(f"JOGO: {result['home']} x {result['away']}")
        print("=" * 50)

        print("\nESTATÍSTICAS")

        for market, values in result["stats"].items():
            print(
                f"{market}: "
                f"Casa {values['home']} | "
                f"Fora {values['away']} | "
                f"Total {values['total']}"
            )

        print("\nPROBABILIDADES")

        for market, values in result["probabilities"].items():
            over = values["over"]
            under = values["under"]

            print(
                f"{market}: "
                f"Mais = {over}% [{classify(over)}] | "
                f"Menos = {under}% [{classify(under)}]"
            )


if __name__ == "__main__":
    main()
