def estimate_shots(game):
    home_shots = game.get("home_avg_shots", 0)
    away_shots = game.get("away_avg_shots", 0)

    home_on_target = game.get("home_avg_shots_on_target", 0)
    away_on_target = game.get("away_avg_shots_on_target", 0)

    return {
        "home": game["home"],
        "away": game["away"],
        "home_shots": home_shots,
        "away_shots": away_shots,
        "home_shots_on_target": home_on_target,
        "away_shots_on_target": away_on_target
    }
