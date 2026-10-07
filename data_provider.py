from datetime import datetime, timedelta

from api_client import FootballAPI
from config import (
    get_analysis_date,
)


api = FootballAPI()


UPCOMING_STATUS = {
    "NS",
    "TBD",
}


def normalize_fixture(fixture):

    fixture_info = fixture.get(
        "fixture",
        {}
    )

    teams = fixture.get(
        "teams",
        {}
    )

    league = fixture.get(
        "league",
        {}
    )

    status = fixture_info.get(
        "status",
        {}
    )

    return {
        "fixture_id": fixture_info.get(
            "id"
        ),

        "date": fixture_info.get(
            "date"
        ),

        "timestamp": fixture_info.get(
            "timestamp"
        ),

        "status": status.get(
            "short"
        ),

        "status_long": status.get(
            "long"
        ),

        "home_id": (
            teams
            .get("home", {})
            .get("id")
        ),

        "home_name": (
            teams
            .get("home", {})
            .get("name")
        ),

        "away_id": (
            teams
            .get("away", {})
            .get("id")
        ),

        "away_name": (
            teams
            .get("away", {})
            .get("name")
        ),

        "league_id": league.get(
            "id"
        ),

        "league_name": league.get(
            "name"
        ),

        "country": league.get(
            "country"
        ),
    }


def get_upcoming_games():

    start_date_text = get_analysis_date()

    start_date = datetime.strptime(
        start_date_text,
        "%Y-%m-%d"
    ).date()

    print()
    print(
        "Buscando jogos do BET-AI"
    )

    print(
        f"Data inicial: "
        f"{start_date}"
    )

    all_games = []

    # Procuramos 3 dias.
    #
    # Isso evita utilizar from/to sem
    # league + season.
    #
    # Também mantém o consumo de API
    # controlado.

    for day_offset in range(3):

        current_date = (
            start_date
            + timedelta(
                days=day_offset
            )
        )

        date_text = (
            current_date.strftime(
                "%Y-%m-%d"
            )
        )

        print()
        print(
            f"Consultando jogos de "
            f"{date_text}"
        )

        try:

            fixtures = api.get(
                "fixtures",
                {
                    "date": date_text,
                    "timezone": (
                        "America/Sao_Paulo"
                    ),
                }
            )

        except Exception as error:

            print(
                f"Erro ao consultar "
                f"{date_text}: {error}"
            )

            continue

        print(
            f"Partidas retornadas: "
            f"{len(fixtures)}"
        )

        for fixture in fixtures:

            game = normalize_fixture(
                fixture
            )

            if not game[
                "fixture_id"
            ]:

                continue

            if game[
                "status"
            ] not in UPCOMING_STATUS:

                continue

            all_games.append(
                game
            )

    # ------------------------------------------------
    # REMOVER DUPLICADOS
    # ------------------------------------------------

    unique_games = {}

    for game in all_games:

        fixture_id = game[
            "fixture_id"
        ]

        unique_games[
            fixture_id
        ] = game

    games = list(
        unique_games.values()
    )

    # ------------------------------------------------
    # ORDENAR POR HORÁRIO
    # ------------------------------------------------

    games.sort(
        key=lambda game: (
            game[
                "timestamp"
            ] or 0
        )
    )

    print()
    print(
        f"Jogos futuros encontrados: "
        f"{len(games)}"
    )

    return games


def get_prediction(
    fixture_id
):

    try:

        result = api.get(
            "predictions",
            {
                "fixture": fixture_id
            }
        )

        if not result:

            print(
                f"Sem previsão disponível "
                f"para fixture "
                f"{fixture_id}."
            )

            return None

        return result[0]

    except Exception as error:

        print(
            f"Previsão indisponível "
            f"para fixture "
            f"{fixture_id}: "
            f"{error}"
        )

        return None


def _float(value):

    try:

        return float(
            str(value)
            .replace(",", ".")
            .strip()
        )

    except Exception:

        return None


def extract_odds(
    odds_response,
    home_name,
    away_name
):

    markets = {

        "match_winner": {},

        "double_chance": {},

        "goals": {},
    }

    if not odds_response:

        return markets

    home_lower = (
        home_name or ""
    ).lower()

    away_lower = (
        away_name or ""
    ).lower()

    for bookmaker in odds_response:

        bookmaker_name = bookmaker.get(
            "name",
            "Desconhecida"
        )

        bets = bookmaker.get(
            "bets",
            []
        )

        for bet in bets:

            bet_id = str(
                bet.get(
                    "id",
                    ""
                )
            )

            bet_name = str(
                bet.get(
                    "name",
                    ""
                )
            ).lower()

            values = bet.get(
                "values",
                []
            )

            is_winner = (
                bet_id == "1"
                or "match winner"
                in bet_name
                or "1x2"
                in bet_name
            )

            is_double = (
                bet_id == "12"
                or "double chance"
                in bet_name
            )

            is_goals = (
                bet_id == "5"
                or "goals over/under"
                in bet_name
                or "over/under"
                in bet_name
            )

            for value in values:

                label = str(
                    value.get(
                        "value",
                        ""
                    )
                ).strip()

                odd = _float(
                    value.get(
                        "odd"
                    )
                )

                if (
                    odd is None
                    or odd <= 1
                ):

                    continue

                normalized = (
                    label.lower()
                )

                # ------------------------------------
                # VENCEDOR
                # ------------------------------------

                if is_winner:

                    key = None

                    if normalized == "home":

                        key = "Casa"

                    elif normalized == "draw":

                        key = "Empate"

                    elif normalized == "away":

                        key = "Fora"

                    elif (
                        normalized
                        == home_lower
                    ):

                        key = "Casa"

                    elif (
                        normalized
                        == away_lower
                    ):

                        key = "Fora"

                    if key:

                        current = markets[
                            "match_winner"
                        ].get(
                            key
                        )

                        if (
                            current is None
                            or odd
                            > current[
                                "odd"
                            ]
                        ):

                            markets[
                                "match_winner"
                            ][key] = {

                                "odd": odd,

                                "bookmaker":
                                    bookmaker_name,
                            }

                # ------------------------------------
                # DUPLA CHANCE
                # ------------------------------------

                elif is_double:

                    key = None

                    if (
                        "home/draw"
                        in normalized
                        or "draw/home"
                        in normalized
                        or normalized == "1x"
                        or "home or draw"
                        in normalized
                    ):

                        key = (
                            "Casa ou Empate"
                        )

                    elif (
                        "draw/away"
                        in normalized
                        or "away/draw"
                        in normalized
                        or normalized == "x2"
                        or "away or draw"
                        in normalized
                    ):

                        key = (
                            "Fora ou Empate"
                        )

                    elif (
                        "home/away"
                        in normalized
                        or "away/home"
                        in normalized
                        or normalized == "12"
                    ):

                        key = (
                            "Casa ou Fora"
                        )

                    if key:

                        current = markets[
                            "double_chance"
                        ].get(
                            key
                        )

                        if (
                            current is None
                            or odd
                            > current[
                                "odd"
                            ]
                        ):

                            markets[
                                "double_chance"
                            ][key] = {

                                "odd": odd,

                                "bookmaker":
                                    bookmaker_name,
                            }

                # ------------------------------------
                # GOLS
                # ------------------------------------

                elif is_goals:

                    current = markets[
                        "goals"
                    ].get(
                        label
                    )

                    if (
                        current is None
                        or odd
                        > current[
                            "odd"
                        ]
                    ):

                        markets[
                            "goals"
                        ][label] = {

                            "odd": odd,

                            "bookmaker":
                                bookmaker_name,
                        }

    return markets


def get_odds(game):

    try:

        response = api.get(
            "odds",
            {
                "fixture":
                    game[
                        "fixture_id"
                    ]
            }
        )

        return extract_odds(
            response,
            game[
                "home_name"
            ],
            game[
                "away_name"
            ]
        )

    except Exception as error:

        print(
            "Odds não disponíveis: "
            f"{error}"
        )

        return {

            "match_winner": {},

            "double_chance": {},

            "goals": {},
        }


def update_finished_fixtures(
    fixture_ids
):

    if not fixture_ids:

        return []

    ids = [
        str(fixture_id)
        for fixture_id in fixture_ids
    ]

    # A API aceita até 20 IDs
    # em uma chamada.

    ids_parameter = "-".join(
        ids[:20]
    )

    try:

        print()
        print(
            "Atualizando resultados "
            "pendentes..."
        )

        return api.get(
            "fixtures",
            {
                "ids":
                    ids_parameter,

                "timezone":
                    "America/Sao_Paulo",
            }
        )

    except Exception as error:

        print(
            "Não foi possível atualizar "
            f"resultados: {error}"
        )

        return []
