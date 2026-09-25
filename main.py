import json

from analyzer import analyze_game
from ticket import generate_ticket


def main():
    with open("data/games.json", "r", encoding="utf-8") as file:
        games = json.load(file)

    results = []

    print("\n===== BET AI V1 =====\n")

    for game in games:
        result = analyze_game(game)
        results.append(result)

        print(f'{result["home"]} x {result["away"]}')
        print(f'Casa: {result["home_probability"]}%')
        print(f'Fora: {result["away_probability"]}%\n')

    ticket = generate_ticket(results)

    print("===== TALÃO SIMULADO =====\n")

    if not ticket:
        print("Nenhuma seleção atingiu o limite.")
        return

    for selection in ticket:
        print(
            f'{selection["game"]} -> '
            f'{selection["selection"]} '
            f'({selection["probability"]}%)'
        )


if __name__ == "__main__":
    main()
