def estimate_cards(game):
    home_cards = game.get("home_avg_cards", 0)
    away_cards = game.get("away_avg_cards", 0)

    total_cards = home_cards + away_cards

    return {
        "home": game["home"],
        "away": game["away"],
        "home_avg_cards": home_cards,
        "away_avg_cards": away_cards,
        "expected_total_cards": round(total_cards, 2)
    }
