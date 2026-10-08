import math


def _number(value):

    try:

        return float(value)

    except Exception:

        return None


def _extract_percent(
    percent_data,
    key
):

    if not isinstance(
        percent_data,
        dict
    ):

        return None

    value = percent_data.get(
        key
    )

    if isinstance(
        value,
        str
    ):

        value = (
            value
            .replace("%", "")
            .strip()
        )

    return _number(
        value
    )


def _poisson_over(
    expected,
    line
):

    if expected is None:

        return None

    probability_under = 0.0

    maximum = 20

    for goals in range(
        maximum + 1
    ):

        probability = (
            math.exp(-expected)
            * expected ** goals
            / math.factorial(goals)
        )

        if goals <= line:

            probability_under += probability

    return max(
        0.0,
        min(
            100.0,
            (1 - probability_under)
            * 100
        )
    )


def _classification(
    probability
):

    if probability >= 75:

        return "ALTA"

    if probability >= 60:

        return "MÉDIA"

    return "BAIXA"


def analyze_game(
    game,
    prediction,
    odds=None,
    memory=None
):

    if not prediction:

        return None

    fixture_id = game.get(
        "fixture_id"
    )

    home = game.get(
        "home",
        "Casa"
    )

    away = game.get(
        "away",
        "Fora"
    )

    predictions = prediction.get(
        "predictions",
        {}
    )

    percent = predictions.get(
        "percent",
        {}
    )

    winner = predictions.get(
        "winner",
        {}
    )

    goals = predictions.get(
        "goals",
        {}
    )

    probabilities = {}

    # ======================================================
    # RESULTADO
    # ======================================================

    home_probability = (
        _extract_percent(
            percent,
            "home"
        )
    )

    draw_probability = (
        _extract_percent(
            percent,
            "draw"
        )
    )

    away_probability = (
        _extract_percent(
            percent,
            "away"
        )
    )

    if home_probability is not None:

        probabilities[
            "Casa"
        ] = home_probability

    if draw_probability is not None:

        probabilities[
            "Empate"
        ] = draw_probability

    if away_probability is not None:

        probabilities[
            "Fora"
        ] = away_probability

    # ======================================================
    # DUPLA CHANCE
    # ======================================================

    if (
        home_probability is not None
        and draw_probability is not None
    ):

        probabilities[
            "Casa ou Empate"
        ] = min(
            99.0,
            home_probability
            + draw_probability
        )

    if (
        home_probability is not None
        and away_probability is not None
    ):

        probabilities[
            "Casa ou Fora"
        ] = min(
            99.0,
            home_probability
            + away_probability
        )

    if (
        draw_probability is not None
        and away_probability is not None
    ):

        probabilities[
            "Empate ou Fora"
        ] = min(
            99.0,
            draw_probability
            + away_probability
        )

    # ======================================================
    # GOLS
    # ======================================================

    expected_home = _number(
        goals.get("home")
    )

    expected_away = _number(
        goals.get("away")
    )

    expected_total = None

    if (
        expected_home is not None
        and expected_away is not None
    ):

        expected_total = (
            expected_home
            + expected_away
        )

    # ======================================================
    # OVER / UNDER
    # ======================================================

    if expected_total is not None:

        over15 = _poisson_over(
            expected_total,
            1
        )

        over25 = _poisson_over(
            expected_total,
            2
        )

        if over15 is not None:

            probabilities[
                "Mais de 1.5 gols"
            ] = over15

            probabilities[
                "Menos de 1.5 gols"
            ] = 100 - over15

        if over25 is not None:

            probabilities[
                "Mais de 2.5 gols"
            ] = over25

            probabilities[
                "Menos de 2.5 gols"
            ] = 100 - over25

    # ======================================================
    # SELEÇÕES
    # ======================================================

    selections = []

    for market, probability in (
        probabilities.items()
    ):

        if probability < 60:

            continue

        selections.append(
            {
                "market": market,

                "probability":
                    round(
                        probability,
                        2
                    ),

                "classification":
                    _classification(
                        probability
                    ),
            }
        )

    selections.sort(
        key=lambda x:
            x["probability"],
        reverse=True
    )

    # ======================================================
    # RESULTADO
    # ======================================================

    winner_name = None

    if isinstance(
        winner,
        dict
    ):

        winner_name = winner.get(
            "name"
        )

    result = {

        "fixture_id":
            fixture_id,

        "home":
            home,

        "away":
            away,

        "winner_prediction":
            winner_name,

        "expected_goals_home":
            expected_home,

        "expected_goals_away":
            expected_away,

        "expected_goals_total":
            expected_total,

        "probabilities":
            probabilities,

        "selections":
            selections,

        "odds":
            odds or [],
    }

    return result
