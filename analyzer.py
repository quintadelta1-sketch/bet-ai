def analyze_game(game):
    home = (
        game["home_form"] * 0.35
        + game["home_strength"] * 0.35
        + min(game["home_avg_goals"] / 2.5, 1) * 0.30
    )

    away = (
        game["away_form"] * 0.35
        + game["away_strength"] * 0.35
        + min(game["away_avg_goals"] / 2.5, 1) * 0.30
    )

    total = home + away

    home_prob = home / total
    away_prob = away / total

    return {
        "home": game["home"],
        "away": game["away"],
        "home_probability": round(home_prob * 100, 2),
        "away_probability": round(away_prob * 100, 2)
    }
