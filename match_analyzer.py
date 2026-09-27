def analyze_match(game):
    home = game["home"]
    away = game["away"]

    # GOLS
    home_goals = game.get("home_avg_goals", 0)
    away_goals = game.get("away_avg_goals", 0)

    # ESCANTEIOS
    home_corners = game.get("home_avg_corners", 0)
    away_corners = game.get("away_avg_corners", 0)

    # CHUTES
    home_shots = game.get("home_avg_shots", 0)
    away_shots = game.get("away_avg_shots", 0)

    # CHUTES NO ALVO
    home_shots_target = game.get("home_avg_shots_on_target", 0)
    away_shots_target = game.get("away_avg_shots_on_target", 0)

    # CARTÕES
    home_cards = game.get("home_avg_cards", 0)
    away_cards = game.get("away_avg_cards", 0)

    # DESARMES
    home_tackles = game.get("home_avg_tackles", 0)
    away_tackles = game.get("away_avg_tackles", 0)

    # INTERCEPTAÇÕES
    home_interceptions = game.get("home_avg_interceptions", 0)
    away_interceptions = game.get("away_avg_interceptions", 0)

    # FALTAS
    home_fouls = game.get("home_avg_fouls", 0)
    away_fouls = game.get("away_avg_fouls", 0)

    # FORÇA GERAL
    home_score = (
        home_goals * 0.25
        + home_corners * 0.10
        + home_shots * 0.15
        + home_shots_target * 0.15
        + home_tackles * 0.10
        + home_interceptions * 0.05
        + home_fouls * 0.05
        + home_cards * 0.05
    )

    away_score = (
        away_goals * 0.25
        + away_corners * 0.10
        + away_shots * 0.15
        + away_shots_target * 0.15
        + away_tackles * 0.10
        + away_interceptions * 0.05
        + away_fouls * 0.05
        + away_cards * 0.05
    )

    total = home_score + away_score

    if total > 0:
        home_probability = (home_score / total) * 100
        away_probability = (away_score / total) * 100
    else:
        home_probability = 0
        away_probability = 0

    return {
        "home": home,
        "away": away,

        "home_probability": round(home_probability, 2),
        "away_probability": round(away_probability, 2),

        "goals": {
            "home": home_goals,
            "away": away_goals
        },

        "corners": {
            "home": home_corners,
            "away": away_corners
        },

        "shots": {
            "home": home_shots,
            "away": away_shots
        },

        "shots_on_target": {
            "home": home_shots_target,
            "away": away_shots_target
        },

        "cards": {
            "home": home_cards,
            "away": away_cards
        },

        "tackles": {
            "home": home_tackles,
            "away": away_tackles
        },

        "interceptions": {
            "home": home_interceptions,
            "away": away_interceptions
        },

        "fouls": {
            "home": home_fouls,
            "away": away_fouls
        }
    }
