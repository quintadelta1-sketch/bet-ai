def estimate_tackles(game):
    home_tackles = game.get("home_avg_tackles", 0)
    away_tackles = game.get("away_avg_tackles", 0)

    home_interceptions = game.get("home_avg_interceptions", 0)
    away_interceptions = game.get("away_avg_interceptions", 0)

    home_clearances = game.get("home_avg_clearances", 0)
    away_clearances = game.get("away_avg_clearances", 0)

    return {
        "home": game["home"],
        "away": game["away"],

        "home_tackles": home_tackles,
        "away_tackles": away_tackles,

        "home_interceptions": home_interceptions,
        "away_interceptions": away_interceptions,

        "home_clearances": home_clearances,
        "away_clearances": away_clearances
    }
