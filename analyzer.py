import math
import re

from memory import calibrate_probability


def percent(value):

    if value is None:
        return None

    text = str(value)

    text = text.replace(
        "%",
        ""
    )

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text
    )

    if not match:
        return None

    try:
        return float(
            match.group()
        )
    except Exception:
        return None


def parse_goal_prediction(value):

    if value is None:
        return None

    if isinstance(
        value,
        (int, float)
    ):
        return float(value)

    text = str(value).strip()

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    if not numbers:
        return None

    values = [
        float(number)
        for number in numbers
    ]

    return sum(values) / len(values)


def poisson_probability(
    goals,
    expected
):

    if expected <= 0:
        return 1.0 if goals == 0 else 0.0

    return (
        math.exp(-expected)
        * expected ** goals
        / math.factorial(goals)
    )


def over_probability(
    expected,
    line
):

    probability_under = 0.0

    max_goals = int(
        math.ceil(line)
    )

    for goals in range(
        max_goals
    ):

        probability_under += (
            poisson_probability(
                goals,
                expected
            )
        )

    return max(
        0.0,
        min(
            1.0,
            1 - probability_under
        )
    ) * 100


def fair_probability_from_odds(
    odds_map
):

    raw = {}

    for key, data in odds_map.items():

        odd = data.get(
            "odd"
        )

        if not odd or odd <= 1:
            continue

        raw[key] = (
            1 / odd
        )

    total = sum(
        raw.values()
    )

    if total <= 0:
        return {}

    return {
        key: (
            value / total
        ) * 100
        for key, value in raw.items()
    }


def implied_probability(
    odd
):

    if not odd or odd <= 1:
        return None

    return (
        1 / odd
    ) * 100


def classify(
    probability,
    edge
):

    if edge is not None:

        if (
            probability >= 65
            and edge >= 5
        ):
            return "VALOR FORTE"

        if (
            probability >= 60
            and edge >= 3
        ):
            return "VALOR"

        if probability >= 75:
            return "PROBABILIDADE ALTA"

        return "OBSERVAR"

    if probability >= 75:
        return "PROBABILIDADE ALTA"

    if probability >= 65:
        return "PROBABILIDADE MÉDIA"

    return "BAIXA"


def add_market(
    markets,
    key,
    name,
    probability,
    source,
    odds_data=None,
    fair_probs=None
):

    if probability is None:
        return

    probability = max(
        0,
        min(
            100,
            probability
        )
    )

    fair = None
    odd = None
    bookmaker = None
    edge = None

    if odds_data:

        data = odds_data.get(
            key
        )

        if data:

            odd = data.get(
                "odd"
            )

            bookmaker = data.get(
                "bookmaker"
            )

            if fair_probs:

                fair = fair_probs.get(
                    name
                )

            if fair is None:

                fair = implied_probability(
                    odd
                )

            if fair is not None:

                edge = (
                    probability - fair
                )

    markets.append({
        "key": key,
        "name": name,
        "probability": round(
            probability,
            2
        ),
        "raw_probability": round(
            probability,
            2
        ),
        "source": source,
        "odd": odd,
        "bookmaker": bookmaker,
        "implied_probability": (
            round(fair, 2)
            if fair is not None
            else None
        ),
        "edge": (
            round(edge, 2)
            if edge is not None
            else None
        ),
        "classification": classify(
            probability,
            edge
        ),
    })


def analyze_game(
    game,
    prediction_payload,
    odds,
    memory
):

    prediction = (
        prediction_payload
        .get("predictions", {})
    )

    percent_data = (
        prediction.get(
            "percent",
            {}
        )
    )

    home_probability = percent(
        percent_data.get("home")
    )

    draw_probability = percent(
        percent_data.get("draw")
    )

    away_probability = percent(
        percent_data.get("away")
    )

    if (
        home_probability is None
        or draw_probability is None
        or away_probability is None
    ):

        raise RuntimeError(
            "A API não forneceu "
            "probabilidades 1X2 suficientes."
        )

    goals = prediction.get(
        "goals",
        {}
    )

    expected_home = (
        parse_goal_prediction(
            goals.get("home")
        )
    )

    expected_away = (
        parse_goal_prediction(
            goals.get("away")
        )
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

    # Calibração usando memória anterior
    home_probability = calibrate_probability(
        home_probability,
        "home",
        memory
    )

    draw_probability = calibrate_probability(
        draw_probability,
        "draw",
        memory
    )

    away_probability = calibrate_probability(
        away_probability,
        "away",
        memory
    )

    fair_1x2 = fair_probability_from_odds(
        odds.get(
            "match_winner",
            {}
        )
    )

    markets = []

    add_market(
        markets,
        "home",
        game["home_name"],
        home_probability,
        "API-Football + calibração BET-AI",
        odds.get(
            "match_winner",
            {}
        ).get("Casa"),
        fair_1x2
    )

    add_market(
        markets,
        "draw",
        "Empate",
        draw_probability,
        "API-Football + calibração BET-AI",
        odds.get(
            "match_winner",
            {}
        ).get("Empate"),
        fair_1x2
    )

    add_market(
        markets,
        "away",
        game["away_name"],
        away_probability,
        "API-Football + calibração BET-AI",
        odds.get(
            "match_winner",
            {}
        ).get("Fora"),
        fair_1x2
    )

    home_draw = (
        home_probability
        + draw_probability
    )

    away_draw = (
        away_probability
        + draw_probability
    )

    home_away = (
        home_probability
        + away_probability
    )

    home_draw = calibrate_probability(
        home_draw,
        "home_draw",
        memory
    )

    away_draw = calibrate_probability(
        away_draw,
        "away_draw",
        memory
    )

    home_away = calibrate_probability(
        home_away,
        "home_away",
        memory
    )

    add_market(
        markets,
        "home_draw",
        "Casa ou Empate",
        home_draw,
        "Derivação BET-AI",
        odds.get(
            "double_chance",
            {}
        ).get("Casa ou Empate")
    )

    add_market(
        markets,
        "away_draw",
        "Fora ou Empate",
        away_draw,
        "Derivação BET-AI",
        odds.get(
            "double_chance",
            {}
        ).get("Fora ou Empate")
    )

    add_market(
        markets,
        "home_away",
        "Casa ou Fora",
        home_away,
        "Derivação BET-AI",
        odds.get(
            "double_chance",
            {}
        ).get("Casa ou Fora")
    )

    if expected_total is not None:

        over_15 = over_probability(
            expected_total,
            1.5
        )

        over_25 = over_probability(
            expected_total,
            2.5
        )

        under_15 = (
            100 - over_15
        )

        under_25 = (
            100 - over_25
        )

        over_15 = calibrate_probability(
            over_15,
            "over_1_5",
            memory
        )

        over_25 = calibrate_probability(
            over_25,
            "over_2_5",
            memory
        )

        under_15 = calibrate_probability(
            under_15,
            "under_1_5",
            memory
        )

        under_25 = calibrate_probability(
            under_25,
            "under_2_5",
            memory
        )

        add_market(
            markets,
            "over_1_5",
            "Mais de 1.5 gols",
            over_15,
            "Poisson BET-AI",
            odds.get(
                "goals",
                {}
            ).get("Over 1.5")
        )

        add_market(
            markets,
            "under_1_5",
            "Menos de 1.5 gols",
            under_15,
            "Poisson BET-AI",
            odds.get(
                "goals",
                {}
            ).get("Under 1.5")
        )

        add_market(
            markets,
            "over_2_5",
            "Mais de 2.5 gols",
            over_25,
            "Poisson BET-AI",
            odds.get(
                "goals",
                {}
            ).get("Over 2.5")
        )

        add_market(
            markets,
            "under_2_5",
            "Menos de 2.5 gols",
            under_25,
            "Poisson BET-AI",
            odds.get(
                "goals",
                {}
            ).get("Under 2.5")
        )

    winner = prediction.get(
        "winner",
        {}
    )

    return {
        "fixture_id": game["fixture_id"],

        "home": game["home_name"],

        "away": game["away_name"],

        "winner": winner.get(
            "name"
        ),

        "winner_comment": winner.get(
            "comment"
        ),

        "advice": prediction.get(
            "advice"
        ),

        "win_or_draw": prediction.get(
            "win_or_draw"
        ),

        "api_under_over": prediction.get(
            "under_over"
        ),

        "expected_goals": {
            "home": expected_home,
            "away": expected_away,
            "total": expected_total,
        },

        "markets": markets,

        "comparison": prediction_payload.get(
            "comparison",
            {}
        ),

        "teams": prediction_payload.get(
            "teams",
            {}
        ),
    }
