import json
import os
from datetime import datetime


MEMORY_FILE = "data/memory.json"


DEFAULT_MEMORY = {
    "created_at": None,
    "updated_at": None,
    "predictions": []
}


def ensure_storage():

    directory = os.path.dirname(
        MEMORY_FILE
    )

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    if not os.path.exists(
        MEMORY_FILE
    ):

        memory = DEFAULT_MEMORY.copy()

        now = datetime.utcnow().isoformat()

        memory["created_at"] = now
        memory["updated_at"] = now

        save_memory(memory)


def load_memory():

    ensure_storage()

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            memory = json.load(file)

        if "predictions" not in memory:

            memory["predictions"] = []

        return memory

    except Exception:

        return DEFAULT_MEMORY.copy()


def save_memory(memory):

    ensure_storage()

    memory["updated_at"] = (
        datetime.utcnow().isoformat()
    )

    temporary_file = (
        MEMORY_FILE + ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            ensure_ascii=False,
            indent=2
        )

    os.replace(
        temporary_file,
        MEMORY_FILE
    )


def fixture_already_saved(
    memory,
    fixture_id
):

    for record in memory["predictions"]:

        if record.get(
            "fixture_id"
        ) == fixture_id:

            return True

    return False


def register_prediction(
    memory,
    game,
    analysis,
    selected
):

    fixture_id = game[
        "fixture_id"
    ]

    if fixture_already_saved(
        memory,
        fixture_id
    ):

        return False

    record = {
        "fixture_id": fixture_id,

        "created_at": datetime.utcnow().isoformat(),

        "game": {
            "home_id": game["home_id"],
            "home_name": game["home_name"],
            "away_id": game["away_id"],
            "away_name": game["away_name"],
            "league_id": game["league_id"],
            "league_name": game["league_name"],
            "country": game["country"],
            "date": game["date"],
        },

        "prediction": {
            "winner": analysis.get(
                "winner"
            ),

            "advice": analysis.get(
                "advice"
            ),

            "api_under_over": analysis.get(
                "api_under_over"
            ),

            "expected_goals": analysis.get(
                "expected_goals"
            ),

            "markets": analysis.get(
                "markets",
                []
            ),
        },

        "selected": selected,

        "result": None,

        "evaluation": None,
    }

    memory["predictions"].append(
        record
    )

    return True


def get_pending_fixture_ids(
    memory
):

    ids = []

    for record in memory["predictions"]:

        if record.get("result") is None:

            fixture_id = record.get(
                "fixture_id"
            )

            if fixture_id:

                ids.append(
                    fixture_id
                )

    return ids


def _actual_outcome(
    home_goals,
    away_goals
):

    if home_goals > away_goals:
        return "home"

    if away_goals > home_goals:
        return "away"

    return "draw"


def _market_hit(
    market_key,
    home_goals,
    away_goals
):

    outcome = _actual_outcome(
        home_goals,
        away_goals
    )

    total_goals = (
        home_goals + away_goals
    )

    if market_key == "home":
        return outcome == "home"

    if market_key == "draw":
        return outcome == "draw"

    if market_key == "away":
        return outcome == "away"

    if market_key == "home_draw":
        return outcome in {
            "home",
            "draw"
        }

    if market_key == "away_draw":
        return outcome in {
            "away",
            "draw"
        }

    if market_key == "home_away":
        return outcome in {
            "home",
            "away"
        }

    if market_key == "over_1_5":
        return total_goals >= 2

    if market_key == "under_1_5":
        return total_goals <= 1

    if market_key == "over_2_5":
        return total_goals >= 3

    if market_key == "under_2_5":
        return total_goals <= 2

    return None


def update_memory_with_results(
    memory,
    fixtures
):

    updated = 0

    fixture_map = {}

    for fixture in fixtures:

        fixture_id = (
            fixture
            .get("fixture", {})
            .get("id")
        )

        if fixture_id:

            fixture_map[
                fixture_id
            ] = fixture

    finished_status = {
        "FT",
        "AET",
        "PEN",
    }

    void_status = {
        "PST",
        "CANC",
        "ABD",
        "SUSP",
    }

    for record in memory["predictions"]:

        if record.get("result") is not None:
            continue

        fixture_id = record.get(
            "fixture_id"
        )

        fixture = fixture_map.get(
            fixture_id
        )

        if not fixture:
            continue

        status = (
            fixture
            .get("fixture", {})
            .get("status", {})
            .get("short")
        )

        if status in void_status:

            record["result"] = {
                "status": status,
                "void": True,
            }

            record["evaluation"] = {
                "void": True,
                "reason": "Partida anulada, suspensa ou adiada.",
            }

            updated += 1

            continue

        if status not in finished_status:
            continue

        score = fixture.get(
            "score",
            {}
        )

        fulltime = score.get(
            "fulltime",
            {}
        )

        home_goals = fulltime.get(
            "home"
        )

        away_goals = fulltime.get(
            "away"
        )

        if (
            home_goals is None
            or away_goals is None
        ):
            continue

        result = {
            "status": status,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "total_goals": (
                home_goals
                + away_goals
            ),
            "outcome": _actual_outcome(
                home_goals,
                away_goals
            ),
            "void": False,
        }

        evaluations = []

        markets = (
            record
            .get("prediction", {})
            .get("markets", [])
        )

        for market in markets:

            key = market.get(
                "key"
            )

            hit = _market_hit(
                key,
                home_goals,
                away_goals
            )

            if hit is None:
                continue

            evaluations.append({
                "key": key,
                "probability": market.get(
                    "probability"
                ),
                "hit": hit,
            })

        record["result"] = result

        record["evaluation"] = {
            "void": False,
            "markets": evaluations,
        }

        updated += 1

    return updated


def get_learning_stats(
    memory
):

    stats = {}

    for record in memory["predictions"]:

        evaluation = record.get(
            "evaluation"
        )

        if not evaluation:
            continue

        if evaluation.get(
            "void"
        ):
            continue

        for item in evaluation.get(
            "markets",
            []
        ):

            key = item.get(
                "key"
            )

            if not key:
                continue

            if key not in stats:

                stats[key] = {
                    "total": 0,
                    "hits": 0,
                    "accuracy": 0.0,
                }

            stats[key]["total"] += 1

            if item.get("hit"):
                stats[key]["hits"] += 1

    for key in stats:

        total = stats[key]["total"]
        hits = stats[key]["hits"]

        if total:

            stats[key]["accuracy"] = (
                hits / total
            ) * 100

    return stats


def calibrate_probability(
    raw_probability,
    market_key,
    memory
):

    stats = get_learning_stats(
        memory
    )

    market_stats = stats.get(
        market_key
    )

    if not market_stats:
        return raw_probability

    total = market_stats[
        "total"
    ]

    accuracy = market_stats[
        "accuracy"
    ]

    if total < 5:
        return raw_probability

    # Quanto mais histórico,
    # maior a influência da experiência real.
    learning_weight = min(
        0.35,
        total / 100
    )

    calibrated = (
        raw_probability
        * (1 - learning_weight)
        + accuracy
        * learning_weight
    )

    return round(
        calibrated,
        2
    )


def memory_summary(memory):

    total = len(
        memory["predictions"]
    )

    completed = 0

    for record in memory["predictions"]:

        if (
            record.get("evaluation")
            and not record["evaluation"].get(
                "void"
            )
        ):
            completed += 1

    return {
        "total_predictions": total,
        "completed": completed,
        "pending": total - completed,
        "learning": get_learning_stats(
            memory
        ),
    }
