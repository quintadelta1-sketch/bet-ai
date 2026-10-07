import time
import requests

from config import (
    API_URL,
    REQUEST_INTERVAL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    MAX_REQUESTS_PER_RUN,
    get_api_key,
)


class FootballAPI:

    def __init__(self):
        self.api_url = API_URL
        self.last_request_time = 0
        self.cache = {}
        self.request_count = 0

    def _wait(self):

        elapsed = time.time() - self.last_request_time

        if elapsed < REQUEST_INTERVAL:

            wait_time = REQUEST_INTERVAL - elapsed

            print(
                f"Aguardando {wait_time:.1f}s "
                f"para respeitar o limite da API..."
            )

            time.sleep(wait_time)

    def get(self, endpoint, params=None):

        params = params or {}

        cache_key = (
            endpoint,
            tuple(sorted(params.items()))
        )

        if cache_key in self.cache:

            print(
                f"Cache utilizado: {endpoint} {params}"
            )

            return self.cache[cache_key]

        if self.request_count >= MAX_REQUESTS_PER_RUN:

            raise RuntimeError(
                "Proteção ativada: limite de chamadas "
                "por execução atingido."
            )

        for attempt in range(MAX_RETRIES + 1):

            self._wait()

            self.request_count += 1

            try:

                print(
                    f"API → {endpoint} {params}"
                )

                response = requests.get(
                    f"{self.api_url}/{endpoint}",
                    headers={
                        "x-apisports-key": get_api_key()
                    },
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                self.last_request_time = time.time()

                remaining = (
                    response.headers.get(
                        "x-ratelimit-requests-remaining"
                    )
                )

                minute_remaining = (
                    response.headers.get(
                        "X-Ratelimit-Remaining"
                    )
                )

                if remaining:
                    print(
                        f"API restante hoje: {remaining}"
                    )

                if minute_remaining:
                    print(
                        f"API restante/minuto: "
                        f"{minute_remaining}"
                    )

                if response.status_code == 429:

                    if attempt >= MAX_RETRIES:

                        raise RuntimeError(
                            "Limite de requisições da API-Football "
                            "atingido."
                        )

                    print(
                        "API retornou 429."
                    )

                    print(
                        "Aguardando 60 segundos..."
                    )

                    time.sleep(60)

                    continue

                try:

                    data = response.json()

                except Exception:

                    raise RuntimeError(
                        "A API retornou uma resposta inválida."
                    )

                if response.status_code != 200:

                    raise RuntimeError(
                        f"Erro HTTP {response.status_code}: "
                        f"{data}"
                    )

                if data.get("errors"):

                    raise RuntimeError(
                        f"Erro da API-Football: "
                        f"{data['errors']}"
                    )

                result = data.get(
                    "response",
                    []
                )

                self.cache[cache_key] = result

                return result

            except requests.RequestException as error:

                if attempt >= MAX_RETRIES:

                    raise RuntimeError(
                        f"Falha de conexão com a API-Football: "
                        f"{error}"
                    )

                print(
                    "Falha temporária."
                )

                print(
                    "Tentando novamente..."
                )

                time.sleep(5)

        raise RuntimeError(
            "Não foi possível consultar a API-Football."
        )
