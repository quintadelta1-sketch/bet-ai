from models.probability_model import calculate_probabilities


def analyze_match(game):

    home = game["home"]
    away = game["away"]

    # =========================
    # ESTATÍSTICAS DA PARTIDA
    # =========================

    stats = {
        "goals": {
            "home": game.get("home_avg_goals", 0),
            "away": game.get("away_avg_goals", 0)
        },

        "corners": {
            "home": game.get("home_avg_corners", 0),
            "away": game.get("away_avg_corners", 0)
        },

        "shots": {
            "home": game.get("home_avg_shots", 0),
            "away": game.get("away_avg_shots", 0)
        },

        "shots_on_target": {
            "home": game.get("home_avg_shots_on_target", 0),
            "away": game.get("away_avg_shots_on_target", 0)
        },

        "tackles": {
            "home": game.get("home_avg_tackles", 0),
            "away": game.get("away_avg_tackles", 0)
        },

        "cards": {
            "home": game.get("home_avg_cards", 0),
            "away": game.get("away_avg_cards", 0)
        },

        "fouls": {
            "home": game.get("home_avg_fouls", 0),
            "away": game.get("away_avg_fouls", 0)
        }
    }

    # =========================
    # TOTAIS
    # =========================

    totals = {}

    for market, values in stats.items():
        totals[market] = round(
            values["home"] + values["away"],
            2
        )

    # =========================
    # PROBABILIDADES
    # =========================

    probabilities = calculate_probabilities(stats)

    # =========================
    # RESULTADO
    # =========================

    return {
        "home": home,
        "away": away,
        "stats": stats,
        "totals": totals,
        "probabilities": probabilities
    }
