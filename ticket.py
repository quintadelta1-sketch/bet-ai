from config import (
    MIN_PROBABILITY,
    MIN_EDGE,
    MAX_SELECTIONS,
)


def generate_ticket(
    markets
):

    with_value = []

    without_value = []

    for market in markets:

        probability = market.get(
            "probability",
            0
        )

        edge = market.get(
            "edge"
        )

        if probability < MIN_PROBABILITY:
            continue

        if (
            edge is not None
            and edge >= MIN_EDGE
        ):

            with_value.append(
                market
            )

        elif edge is None:

            if (
                probability
                >= 75
            ):

                without_value.append(
                    market
                )

    if with_value:

        with_value.sort(
            key=lambda x: (
                x.get("edge") or 0,
                x.get("probability") or 0,
            ),
            reverse=True
        )

        return {
            "mode": "VALOR",
            "selections": with_value[
                :MAX_SELECTIONS
            ],
        }

    without_value.sort(
        key=lambda x: (
            x.get("probability") or 0
        ),
        reverse=True
    )

    return {
        "mode": "PROBABILIDADE",
        "selections": without_value[
            :MAX_SELECTIONS
        ],
    }
