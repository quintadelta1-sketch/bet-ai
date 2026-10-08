import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE


MEMORY_FILE = "data/memory.json"


def _empty_memory():

    return {
        "version": 1,

        "predictions": [],

        "results": [],

        "learning": {},

        "updated_at": None,
    }


def _ensure_file():

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(
        MEMORY_FILE
    ):

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                _empty_memory(),
                file,
                ensure_ascii=False,
                indent=2
            )


def load_memory():

    _ensure_file()

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

    except Exception:

        data = _empty_memory()

    if not isinstance(
        data,
        dict
    ):

        data = _empty_memory()

    data.setdefault(
        "version",
        1
    )

    data.setdefault(
        "predictions",
        []
    )

    data.setdefault(
        "results",
        []
    )

    data.setdefault(
        "learning",
        {}
    )

    data.setdefault(
        "updated_at",
        None
    )

    return data


def save_memory(
    memory
):

    _ensure_file()

    memory[
        "updated_at"
    ] = datetime.now(
        ZoneInfo(TIMEZONE)
    ).isoformat()

    temporary = (
        MEMORY_FILE
        + ".tmp"
    )

    with open(
        temporary,
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
        temporary,
        MEMORY_FILE
    )


def register_prediction(
    memory,
    fixture_id,
    game,
    prediction,
    selected_ticket
):

    fixture_id = int(
        fixture_id
    )

    predictions = memory[
        "predictions"
    ]

    for item in predictions:

        if (
            item.get(
                "fixture_id"
            )
            == fixture_id
        ):

            return

    predictions.append(
        {
            "fixture_id":
                fixture_id,

            "created_at":
                datetime.now(
                    ZoneInfo(
                        TIMEZONE
                    )
                ).isoformat(),

            "game":
                game,

            "prediction":
                prediction,

            "ticket":
                selected_ticket or [],

            "status":
                "pending",

            "result":
                None,
        }
    )


def _evaluate_market(
    market,
    result
):

    # Nesta primeira base,
    # só avaliamos automaticamente
    # mercados de gols e resultado.
    #
    # Mercados que não possuem dados suficientes
    # permanecem sem avaliação.

    home_goals = None
    away_goals = None

    fixture = result.get(
        "fixture",
        {}
    )

    goals = result.get(
        "goals",
        {}
    )

    if isinstance(
        goals,
        dict
    ):

        home_goals = goals.get(
            "home"
        )

        away_goals = goals.get(
            "away"
        )

    if (
        home_goals is None
        or away_goals is None
    ):

        return None

    try:

        home_goals = int(
            home_goals
        )

        away_goals = int(
            away_goals
        )

    except Exception:

        return None

    total = (
        home_goals
        + away_goals
    )

    if market == "Mais de 1.5 gols":

        return total >= 2

    if market == "Menos de 1.5 gols":

        return total <= 1

    if market == "Mais de 2.5 gols":

        return total >= 3

    if market == "Menos de 2.5 gols":

        return total <= 2

    if market == "Casa":

        return home_goals > away_goals

    if market == "Empate":

        return home_goals == away_goals

    if market == "Fora":

        return away_goals > home_goals

    if market == "Casa ou Empate":

        return home_goals >= away_goals

    if market == "Casa ou Fora":

        return home_goals != away_goals

    if market == "Empate ou Fora":

        return away_goals >= home_goals

    return None


def update_finished_fixtures():

    """
    A atualização dos resultados é feita apenas
    quando existem previsões pendentes.

    Usa a API diretamente para evitar
    dependência circular entre módulos.
    """

    memory = load_memory()

    pending = [
        item
        for item in memory[
            "predictions"
        ]
        if item.get(
            "status"
        ) == "pending"
    ]

    if not pending:

        return

    # Importação local para evitar
    # circular import.
    from data_provider import (
        FootballDataProvider
    )

    provider = FootballDataProvider()

    changed = False

    for item in pending:

        fixture_id = item.get(
            "fixture_id"
        )

        if fixture_id is None:

            continue

        try:

            result = provider.get_fixture(
                fixture_id
            )

        except Exception as error:

            print(
                f"Erro no histórico "
                f"{fixture_id}: "
                f"{error}"
            )

            continue

        if not result:

            continue

        status = (
            result
            .get("fixture", {})
            .get("status", {})
            .get("short")
        )

        if status not in (
            "FT",
            "AET",
            "PEN",
        ):

            continue

        item[
            "status"
        ] = "completed"

        item[
            "result"
        ] = result

        item[
            "completed_at"
        ] = datetime.now(
            ZoneInfo(TIMEZONE)
        ).isoformat()

        # Avaliar seleções
        analysis = item.get(
            "prediction",
            {}
        )

        selections = analysis.get(
            "selections",
            []
        )

        for selection in selections:

            market = selection.get(
                "market"
            )

            hit = _evaluate_market(
                market,
                result
            )

            if hit is None:

                continue

            learning = memory[
                "learning"
            ]

            market_data = learning.setdefault(
                market,
                {
                    "total": 0,
                    "hits": 0,
                    "accuracy": 0.0,
                }
            )

            market_data[
                "total"
            ] += 1

            if hit:

                market_data[
                    "hits"
                ] += 1

            market_data[
                "accuracy"
            ] = (
                market_data["hits"]
                /
                market_data["total"]
                * 100
            )

        changed = True

    if changed:

        save_memory(
            memory
        )


def get_learning_stats(
    memory
):

    return memory.get(
        "learning",
        {}
    )
