from config import (
    TIMEZONE,
    MAX_GAMES,
    get_search_dates,
)

from api_client import FootballAPI


class FootballDataProvider:

    def __init__(self):

        self.api = FootballAPI()

    # ======================================================
    # JOGOS FUTUROS
    # ======================================================

    def get_upcoming_games(self):

        games = []

        seen = set()

        dates = get_search_dates(4)

        for date in dates:

            if len(games) >= MAX_GAMES:

                break

            print()

            print(
                f"Buscando jogos de {date}"
            )

            response = self.api.get(
                "fixtures",
                {
                    "date": date,
                    "timezone": TIMEZONE,
                }
            )

            fixtures = response.get(
                "response",
                []
            )

            for item in fixtures:

                fixture = item.get(
                    "fixture",
                    {}
                )

                teams = item.get(
                    "teams",
                    {}
                )

                league = item.get(
                    "league",
                    {}
                )

                fixture_id = fixture.get(
                    "id"
                )

                if fixture_id is None:

                    continue

                fixture_id = int(
                    fixture_id
                )

                if fixture_id in seen:

                    continue

                status = (
                    fixture
                    .get("status", {})
                    .get("short")
                )

                if status not in (
                    "NS",
                    "TBD",
                ):

                    continue

                home = teams.get(
                    "home",
                    {}
                )

                away = teams.get(
                    "away",
                    {}
                )

                game = {

                    "fixture_id":
                        fixture_id,

                    "fixture":
                        fixture,

                    "teams":
                        teams,

                    "league":
                        league,

                    "home":
                        home.get(
                            "name",
                            "Desconhecido"
                        ),

                    "away":
                        away.get(
                            "name",
                            "Desconhecido"
                        ),

                    "home_id":
                        home.get("id"),

                    "away_id":
                        away.get("id"),

                    "date":
                        fixture.get("date"),

                    "timestamp":
                        fixture.get(
                            "timestamp"
                        ),

                    "status":
                        status,

                    "league_id":
                        league.get("id"),

                    "league_name":
                        league.get("name"),

                    "season":
                        league.get("season"),
                }

                seen.add(
                    fixture_id
                )

                games.append(
                    game
                )

                print(
                    f"Encontrado: "
                    f"{game['home']} x "
                    f"{game['away']} "
                    f"({fixture_id})"
                )

                if len(games) >= MAX_GAMES:

                    break

        games.sort(
            key=lambda x:
                x.get(
                    "timestamp",
                    9999999999
                )
        )

        print()

        print(
            f"Jogos selecionados: "
            f"{len(games)}"
        )

        return games

    # ======================================================
    # PREVISÃO
    # ======================================================

    def get_prediction(
        self,
        fixture_id
    ):

        response = self.api.get(
            "predictions",
            {
                "fixture":
                    int(fixture_id)
            }
        )

        data = response.get(
            "response",
            []
        )

        if not data:

            return None

        return data[0]

    # ======================================================
    # ODDS
    # ======================================================

    def get_odds(
        self,
        fixture_id
    ):

        try:

            response = self.api.get(
                "odds",
                {
                    "fixture":
                        int(fixture_id)
                }
            )

            return response.get(
                "response",
                []
            )

        except Exception as error:

            print(
                f"Odds não disponíveis: "
                f"{error}"
            )

            return []

    # ======================================================
    # RESULTADO
    # ======================================================

    def get_fixture(
        self,
        fixture_id
    ):

        response = self.api.get(
            "fixtures",
            {
                "id":
                    int(fixture_id)
            }
        )

        data = response.get(
            "response",
            []
        )

        if not data:

            return None

        return data[0]
