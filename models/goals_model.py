def estimate_goals(game):
    home_avg_goals = game.get("home_avg_goals", 0)
    away_avg_goals = game.get("away_avg_goals", 0)

    total_goals = home_avg_goals + away_avg_goals

    return {
        "home": game["home"],
        "away": game["away"],
        "home_avg_goals": home_avg_goals,
        "away_avg_goals": away_avg_goals,
        "expected_total_goals": round(total_goals, 2)
    }
