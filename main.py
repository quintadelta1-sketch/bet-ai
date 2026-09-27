import json

from match_analyzer import analyze_match


def main():

    with open("data/matches.json", "r", encoding="utf-8") as file:
        matches = json.load(file)

    print("\n===== BET-AI V2 =====\n")

    for game in matches:

        result = analyze_match(game)

        print("=" * 50)
        print(f"JOGO: {result['home']} x {result['away']}")
        print("=" * 50)

        print("\nGOLS")
        print(f"Casa: {result['home_goals']}")
        print(f"Fora: {result['away_goals']}")

        print("\nESCANTEIOS")
        print(f"Casa: {result['home_corners']}")
        print(f"Fora: {result['away_corners']}")

        print("\nCHUTES")
        print(f"Casa: {result['home_shots']}")
        print(f"Fora: {result['away_shots']}")

        print("\nCHUTES NO ALVO")
        print(f"Casa: {result['home_shots_on_target']}")
        print(f"Fora: {result['away_shots_on_target']}")

        print("\nDESARMES")
        print(f"Casa: {result['home_tackles']}")
        print(f"Fora: {result['away_tackles']}")

        print("\nFALTAS")
        print(f"Casa: {result['home_fouls']}")
        print(f"Fora: {result['away_fouls']}")

        print("\nCARTÕES")
        print(f"Casa: {result['home_cards']}")
        print(f"Fora: {result['away_cards']}")

        print()


if __name__ == "__main__":
    main()
