import json

from match_analyzer import analyze_match


def main():

    with open("data/matches.json", "r", encoding="utf-8") as file:
        matches = json.load(file)

    print("\n========== BET-AI V3 ==========\n")

    for game in matches:

        result = analyze_match(game)

        print("=" * 50)
        print(f"JOGO: {result['home']} x {result['away']}")
        print("=" * 50)

        print("\nESTATÍSTICAS")

        for market, values in result["stats"].items():

            print(
                f"{market}: "
                f"Casa {values['home']} | "
                f"Fora {values['away']} | "
                f"Total {result['totals'][market]}"
            )

        print("\nPROBABILIDADES")

        for market, probability in result["probabilities"].items():

            print(
                f"{market}: "
                f"Mais de {probability['line']} = "
                f"{probability['over']}% | "
                f"Menos de {probability['line']} = "
                f"{probability['under']}%"
            )

        print()


if __name__ == "__main__":
    main()
