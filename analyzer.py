import math

from config import (
    MIN_PROBABILITY,
    HIGH_PROBABILITY
)

from data_provider import (
    calculate_team_form
)


# ============================================================
# POISSON
# ============================================================

def poisson_probability(
    goals,
    expected_goals
):

    if expected_goals <= 0:

        return 0.0

    return (
        math.exp(-expected_goals)
        * (
            expected_goals
            ** goals
        )
        / math.factorial(goals)
    )


def probability_over_goals(
    expected_goals,
    line
):

    # Para linha 1.5:
    # P(mais de 1.5) = P(2 ou mais)

    minimum_goals = (
        int(line) + 1
    )

    probability_under = 0

    for goals in range(
        minimum_goals
    ):

        probability_under += (
            poisson_probability(
                goals,
                expected_goals
            )
        )

    probability_over = (
        1 - probability_under
    )

    return round(
        max(
            0,
            min(
                1,
                probability_over
            )
        ) * 100,
        2
    )


# ============================================================
# PROBABILIDADE 1X2
# ============================================================

def calculate_match_probability(
    home_form,
    away_form
):

    home_strength = (
        home_form["form"]
        * 0.65
        + 0.35
    )

    away_strength = (
        away_form["form"]
        * 0.65
    )

    total = (
        home_strength
        + away_strength
    )

    if total <= 0:

        return {
            "home": 33.33,
            "draw": 33.33,
            "away": 33.34
        }

    home = (
        home_strength
        / total
    )

    away = (
        away_strength
        / total
    )

    # Estimativa simples de empate
    draw = 0.25

    remaining = (
        1 - draw
    )

    home *= (
        remaining
        / (home + away)
    )

    away *= (
        remaining
        / (home + away)
    )

    return {

        "home":
            round(
                home * 100,
                2
            ),

        "draw":
            round(
                draw * 100,
                2
            ),

        "away":
            round(
                away * 100,
                2
            )
    }


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classify_probability(
    probability
):

    if probability >= HIGH_PROBABILITY:

        return "ALTA"

    if probability >= MIN_PROBABILITY:

        return "MÉDIA"

    return "BAIXA"


# ============================================================
# ANÁLISE COMPLETA
# ============================================================

def analyze_game(game):

    home_id = game["home_id"]
    away_id = game["away_id"]

    season = game["season"]

    print()
    print(
        f"Analisando: "
        f"{game['home']} x "
        f"{game['away']}"
    )

    print(
        f"Temporada: {season}"
    )

    # --------------------------------------------------------
    # HISTÓRICO CASA
    # --------------------------------------------------------

    print(
        "Buscando histórico da "
        "equipe da casa..."
    )

    home_form = calculate_team_form(

        team_id=home_id,

        season=season,

        games_required=10
    )

    print(
        "Histórico da casa obtido."
    )

    # --------------------------------------------------------
    # HISTÓRICO FORA
    # --------------------------------------------------------

    print(
        "Buscando histórico da "
        "equipe visitante..."
    )

    away_form = calculate_team_form(

        team_id=away_id,

        season=season,

        games_required=10
    )

    print(
        "Histórico do visitante obtido."
    )

    # --------------------------------------------------------
    # PROBABILIDADE 1X2
    # --------------------------------------------------------

    match_probability = (
        calculate_match_probability(
            home_form,
            away_form
        )
    )

    # --------------------------------------------------------
    # EXPECTATIVA DE GOLS
    # --------------------------------------------------------

    expected_home_goals = (

        home_form["goals_for_avg"]
        + away_form["goals_against_avg"]
    ) / 2

    expected_away_goals = (

        away_form["goals_for_avg"]
        + home_form["goals_against_avg"]
    ) / 2

    expected_total_goals = (
        expected_home_goals
        + expected_away_goals
    )

    # --------------------------------------------------------
    # MERCADOS DE GOLS
    # --------------------------------------------------------

    over_15 = probability_over_goals(
        expected_total_goals,
        1.5
    )

    over_25 = probability_over_goals(
        expected_total_goals,
        2.5
    )

    # --------------------------------------------------------
    # MERCADOS
    # --------------------------------------------------------

    markets = [

        {
            "market": "Casa",
            "probability":
                match_probability["home"]
        },

        {
            "market": "Empate",
            "probability":
                match_probability["draw"]
        },

        {
            "market": "Fora",
            "probability":
                match_probability["away"]
        },

        {
            "market": "Casa ou Empate",
            "probability":
                round(
                    match_probability["home"]
                    + match_probability["draw"],
                    2
                )
        },

        {
            "market": "Fora ou Empate",
            "probability":
                round(
                    match_probability["away"]
                    + match_probability["draw"],
                    2
                )
        },

        {
            "market": "Mais de 1.5 gols",
            "probability":
                over_15
        },

        {
            "market": "Mais de 2.5 gols",
            "probability":
                over_25
        }
    ]

    # --------------------------------------------------------
    # CLASSIFICAÇÃO
    # --------------------------------------------------------

    for market in markets:

        market["classification"] = (
            classify_probability(
                market["probability"]
            )
        )

    return {

        "fixture_id":
            game["fixture_id"],

        "home":
            game["home"],

        "away":
            game["away"],

        "league":
            game["league"],

        "season":
            season,

        "date":
            game["date"],

        "home_form":
            home_form,

        "away_form":
            away_form,

        "expected_home_goals":
            round(
                expected_home_goals,
                2
            ),

        "expected_away_goals":
            round(
                expected_away_goals,
                2
            ),

        "expected_total_goals":
            round(
                expected_total_goals,
                2
            ),

        "probabilities":
            match_probability,

        "markets":
            markets
    }
