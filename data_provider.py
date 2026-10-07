from datetime import datetime, timedelta

from config import (
    TIMEZONE,
    MAX_GAMES,
    get_analysis_date,
)

from api_client import FootballAPI


class FootballDataProvider:
    """
    Camada responsável por conversar com a API-Football.

    O restante do BET-AI não precisa conhecer os detalhes
    dos endpoints da API.
    """

    def __init__(self):
        self.api = FootballAPI()

    # ==========================================================
    # REQUISIÇÃO
    # ==========================================================

    def _request(self, endpoint, params=None):
        """
        Compatibilidade com diferentes versões do api_client.py.
        """

        params = params or {}

        # Versão atual esperada
        if hasattr(self.api, "get"):
            return self.api.get(
                endpoint,
                params=params
            )

        # Caso o cliente tenha api_get()
        if hasattr(self.api, "api_get"):
            return self.api.api_get(
                endpoint,
                params=params
            )

        raise RuntimeError(
            "FootballAPI não possui método get/api_get."
        )

    # ==========================================================
    # NORMALIZAÇÃO DO JOGO
    # ==========================================================

    def _normalize_fixture(self, fixture):
        """
        Transforma o retorno da API em um formato único
        usado pelo BET-AI.
        """

        fixture_data = fixture.get(
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

        home = teams.get(
            "home",
            {}
        )

        away = teams.get(
            "away",
            {}
        )

        fixture_id = fixture_data.get("id")

        if fixture_id is None:
            return None

        return {
            "fixture_id": int(fixture_id),

            "id": int(fixture_id),

            "fixture": fixture_data,

            "teams": teams,

            "league": league,

            "home": home.get(
                "name",
                "Desconhecido"
            ),

            "away": away.get(
                "name",
                "Desconhecido"
            ),

            "home_id": home.get(
                "id"
            ),

            "away_id": away.get(
                "id"
            ),

            "date": fixture_data.get(
                "date"
            ),

            "timestamp": fixture_data.get(
                "timestamp"
            ),

            "status": (
                fixture_data
                .get("status", {})
                .get("short")
            ),

            "league_id": league.get(
                "id"
            ),

            "league_name": league.get(
                "name"
            ),

            "season": league.get(
                "season"
            ),
        }

    # ==========================================================
    # JOGOS FUTUROS
    # ==========================================================

    def get_upcoming_games(self):
        """
        Busca jogos futuros começando pela data de análise.

        Em vez de usar from/to, fazemos consultas por dia:

        fixtures?date=YYYY-MM-DD

        Isso evita o problema apresentado anteriormente
        pela API-Football com os parâmetros from/to.
        """

        start_text = get_analysis_date()

        try:
            start_date = datetime.strptime(
                start_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            raise RuntimeError(
                f"ANALYSIS_DATE inválida: {start_text}"
            )

        games = []
        seen = set()

        # Procuramos até 4 dias.
        # Normalmente 3 chamadas já são suficientes,
        # mas deixamos uma margem para dias com poucos jogos.
        for offset in range(4):

            current_date = (
                start_date +
                timedelta(days=offset)
            )

            date_text = current_date.strftime(
                "%Y-%m-%d"
            )

            print(
                f"Buscando jogos de {date_text}..."
            )

            try:

                response = self._request(
                    "fixtures",
                    {
                        "date": date_text,
                        "timezone": TIMEZONE,
                    }
                )

            except Exception as error:

                print(
                    f"Aviso ao consultar "
                    f"{date_text}: {error}"
                )

                continue

            if not isinstance(response, dict):
                continue

            fixtures = response.get(
                "response",
                []
            )

            if not isinstance(fixtures, list):
                continue

            for fixture in fixtures:

                game = self._normalize_fixture(
                    fixture
                )

                if game is None:
                    continue

                fixture_id = game[
                    "fixture_id"
                ]

                if fixture_id in seen:
                    continue

                status = game.get(
                    "status"
                )

                # Somente jogos que ainda não começaram.
                if status not in (
                    "NS",
                    "TBD",
                    "PST",
                ):
                    continue

                seen.add(fixture_id)
                games.append(game)

                if len(games) >= MAX_GAMES:
                    break

            if len(games) >= MAX_GAMES:
                break

        # Ordena cronologicamente
        games.sort(
            key=lambda item: (
                item.get("timestamp")
                or 9999999999
            )
        )

        print(
            f"Jogos selecionados: "
            f"{len(games)}"
        )

        for game in games:

            print(
                f"  {game['fixture_id']} | "
                f"{game['home']} x "
                f"{game['away']}"
            )

        return games

    # ==========================================================
    # PREVISÃO
    # ==========================================================

    def get_prediction(self, fixture_id):
        """
        Obtém a previsão da API-Football.
        """

        fixture_id = int(fixture_id)

        print(
            f"Buscando previsão da partida "
            f"{fixture_id}..."
        )

        response = self._request(
            "predictions",
            {
                "fixture": fixture_id
            }
        )

        if not isinstance(response, dict):
            return None

        data = response.get(
            "response",
            []
        )

        if not data:
            print(
                "Nenhuma previsão disponível."
            )

            return None

        return data[0]

    # ==========================================================
    # ODDS
    # ==========================================================

    def get_odds(self, fixture_id):
        """
        Obtém odds pré-jogo.

        A ausência de odds não impede a análise.
        """

        fixture_id = int(fixture_id)

        print(
            f"Buscando odds da partida "
            f"{fixture_id}..."
        )

        try:

            response = self._request(
                "odds",
                {
                    "fixture": fixture_id
                }
            )

        except Exception as error:

            print(
                f"Odds indisponíveis: {error}"
            )

            return None

        if not isinstance(response, dict):
            return None

        return response.get(
            "response",
            []
        )

    # ==========================================================
    # RESULTADO DE UMA PARTIDA
    # ==========================================================

    def get_fixture(self, fixture_id):
        """
        Consulta uma partida específica.
        """

        fixture_id = int(fixture_id)

        response = self._request(
            "fixtures",
            {
                "id": fixture_id
            }
        )

        if not isinstance(response, dict):
            return None

        data = response.get(
            "response",
            []
        )

        if not data:
            return None

        return data[0]

    # ==========================================================
    # RESULTADOS EM LOTE
    # ==========================================================

    def get_finished_fixtures(
        self,
        fixture_ids
    ):
        """
        Consulta partidas anteriores em pequenos lotes.
        """

        if not fixture_ids:
            return []

        results = []

        # API aceita consulta por IDs separados por "-"
        # para reduzir chamadas.
        for start in range(
            0,
            len(fixture_ids),
            20
        ):

            batch = fixture_ids[
                start:start + 20
            ]

            ids_text = "-".join(
                str(int(x))
                for x in batch
            )

            try:

                response = self._request(
                    "fixtures",
                    {
                        "ids": ids_text
                    }
                )

            except Exception as error:

                print(
                    f"Erro consultando resultados: "
                    f"{error}"
                )

                continue

            if not isinstance(response, dict):
                continue

            data = response.get(
                "response",
                []
            )

            if isinstance(data, list):
                results.extend(data)

        return results

    # ==========================================================
    # ESTATÍSTICAS DE UMA PARTIDA
    # ==========================================================

    def get_statistics(self, fixture_id):
        """
        Obtém estatísticas da partida.

        Só será usada quando necessário.
        """

        fixture_id = int(fixture_id)

        response = self._request(
            "fixtures/statistics",
            {
                "fixture": fixture_id
            }
        )

        if not isinstance(response, dict):
            return []

        return response.get(
            "response",
            []
        )
