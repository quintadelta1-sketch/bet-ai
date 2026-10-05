import time
import requests

from config import (
    API_URL,
    REQUEST_INTERVAL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    get_api_key
)


class FootballAPI:

    def __init__(self):

        self.api_url = API_URL
        self.last_request_time = 0

        # Cache durante a execução
        self.cache = {}

    # ========================================================
    # CONTROLE DE VELOCIDADE
    # ========================================================

    def _wait_before_request(self):

        elapsed = (
            time.time()
            - self.last_request_time
        )

        if elapsed < REQUEST_INTERVAL:

            wait_time = (
                REQUEST_INTERVAL
                - elapsed
            )

            print(
                f"Aguardando {wait_time:.1f}s "
                "para respeitar o limite da API..."
            )

            time.sleep(wait_time)

    # ========================================================
    # REQUISIÇÃO
    # ========================================================

    def get(self, endpoint, params=None):

        params = params or {}

        # Chave do cache
        cache_key = (
            endpoint,
            tuple(
                sorted(
                    params.items()
                )
            )
        )

        # ----------------------------------------------------
        # CACHE
        # ----------------------------------------------------

        if cache_key in self.cache:

            print(
                f"Cache utilizado: "
                f"{endpoint}"
            )

            return self.cache[cache_key]

        # ----------------------------------------------------
        # TENTATIVAS
        # ----------------------------------------------------

        for attempt in range(
            MAX_RETRIES + 1
        ):

            self._wait_before_request()

            try:

                print(
                    f"API → {endpoint} "
                    f"{params}"
                )

                response = requests.get(

                    f"{self.api_url}/{endpoint}",

                    headers={
                        "x-apisports-key":
                            get_api_key()
                    },

                    params=params,

                    timeout=REQUEST_TIMEOUT
                )

                self.last_request_time = (
                    time.time()
                )

                # --------------------------------------------
                # LIMITE DA API
                # --------------------------------------------

                if response.status_code == 429:

                    if attempt >= MAX_RETRIES:

                        raise RuntimeError(
                            "Limite de requisições "
                            "da API-Football atingido. "
                            "Tente novamente mais tarde."
                        )

                    print(
                        "API retornou 429. "
                        "Aguardando 60 segundos..."
                    )

                    time.sleep(60)

                    continue

                # --------------------------------------------
                # RESPOSTA JSON
                # --------------------------------------------

                try:

                    data = response.json()

                except Exception:

                    raise RuntimeError(
                        "A API retornou uma "
                        "resposta que não é JSON."
                    )

                # --------------------------------------------
                # ERRO HTTP
                # --------------------------------------------

                if response.status_code != 200:

                    raise RuntimeError(
                        f"Erro HTTP "
                        f"{response.status_code}: "
                        f"{data}"
                    )

                # --------------------------------------------
                # ERROS DA API
                # --------------------------------------------

                if data.get("errors"):

                    raise RuntimeError(
                        "Erro da API-Football: "
                        f"{data['errors']}"
                    )

                result = data.get(
                    "response",
                    []
                )

                # --------------------------------------------
                # CACHE
                # --------------------------------------------

                self.cache[
                    cache_key
                ] = result

                return result

            except requests.RequestException as error:

                if attempt >= MAX_RETRIES:

                    raise RuntimeError(
                        f"Falha de conexão com "
                        f"a API-Football: {error}"
                    )

                print(
                    "Falha temporária de conexão. "
                    "Tentando novamente..."
                )

                time.sleep(5)

        raise RuntimeError(
            "Não foi possível consultar "
            "a API-Football."
        )
