def _probability(selection):

    if not isinstance(
        selection,
        dict
    ):

        return 0.0

    try:

        return float(
            selection.get(
                "probability",
                0
            )
        )

    except Exception:

        return 0.0


def build_ticket(
    analyses,
    min_probability=60.0,
    max_selections=3
):

    candidates = []

    for analysis in analyses:

        if not isinstance(
            analysis,
            dict
        ):

            continue

        fixture_id = analysis.get(
            "fixture_id"
        )

        home = analysis.get(
            "home",
            "Casa"
        )

        away = analysis.get(
            "away",
            "Fora"
        )

        selections = analysis.get(
            "selections",
            []
        )

        for selection in selections:

            if not isinstance(
                selection,
                dict
            ):

                continue

            probability = _probability(
                selection
            )

            if probability < min_probability:

                continue

            candidates.append(
                {
                    "fixture_id":
                        fixture_id,

                    "home":
                        home,

                    "away":
                        away,

                    "market":
                        selection.get(
                            "market"
                        ),

                    "probability":
                        probability,

                    "classification":
                        selection.get(
                            "classification",
                            "MÉDIA"
                        ),
                }
            )

    candidates.sort(
        key=lambda x:
            x["probability"],
        reverse=True
    )

    # Evita colocar vários mercados
    # da mesma partida no mesmo bilhete.
    selected = []

    used_fixtures = set()

    for item in candidates:

        fixture_id = item.get(
            "fixture_id"
        )

        if fixture_id in used_fixtures:

            continue

        selected.append(
            item
        )

        used_fixtures.add(
            fixture_id
        )

        if len(selected) >= max_selections:

            break

    return selected
