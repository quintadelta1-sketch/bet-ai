import time
import requests

from config import (
    API_URL,
    get_api_key,
    REQUEST_INTERVAL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    MAX_REQUESTS_PER_RUN,
)


class FootballAPI:

    def __init__(self):

        self.base_url = API_URL

        self.headers = {
            "x-apisports-key": get_api_key()
        }

        self.last_request = 0

        self.request_count = 0

        self.cache = {}

    def _wait(self):

        elapsed = (
            time.time()
            - self.last_request
        )

        if elapsed < REQUEST_INTERVAL:

            wait = (
                REQUEST_INTERVAL
                - elapsed
            )

            print(
                f"Aguardando "
                f"{wait:.1f}s para "
                f"respeitar o limite da API..."
            )

            time.sleep(wait)

    def get(
        self,
        endpoint,
        params=None
    ):

        params = params or {}

        cache_key = (
            endpoint,
            tuple(
                sorted(
                    params.items()
                )
            )
        )

        if cache_key in self.cache:

            return self.cache[
                cache_key
            ]

        if (
            self.request_count
            >= MAX_REQUESTS_PER_RUN
        ):

            raise RuntimeError(
                "Limite de requisições "
                "desta execução atingido."
            )

        self._wait()

        url = (
            self.base_url.rstrip("/")
            + "/"
            + endpoint.lstrip("/")
        )

        last_error = None

        for attempt in range(
            MAX_RETRIES + 1
        ):

            try:

                self.request_count += 1

                print(
                    f"API → {endpoint} "
                    f"{params}"
                )

                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                self.last_request = time.time()

                remaining_day = (
                    response.headers.get(
                        "x-ratelimit-requests-remaining"
                    )
                )

                remaining_minute = (
                    response.headers.get(
                        "x-ratelimit-requests-remaining-minute"
                    )
                )

                if remaining_day:

                    print(
                        f"API restante hoje: "
                        f"{remaining_day}"
                    )

                if remaining_minute:

                    print(
                        f"API restante/minuto: "
                        f"{remaining_minute}"
                    )

                if response.status_code == 429:

                    print(
                        "API informou limite "
                        "de requisições."
                    )

                    if attempt < MAX_RETRIES:

                        time.sleep(60)

                        continue

                    raise RuntimeError(
                        "Rate limit da API-Football atingido."
                    )

                if response.status_code != 200:

                    raise RuntimeError(
                        f"HTTP {response.status_code}: "
                        f"{response.text[:500]}"
                    )

                try:

                    data = response.json()

                except Exception:

                    raise RuntimeError(
                        "A API retornou "
                        "JSON inválido."
                    )

                errors = data.get(
                    "errors"
                )

                if errors:

                    if isinstance(
                        errors,
                        dict
                    ) and errors:

                        raise RuntimeError(
                            f"Erro da API-Football: "
                            f"{errors}"
                        )

                self.cache[
                    cache_key
                ] = data

                return data

            except requests.RequestException as error:

                last_error = error

                print(
                    f"Erro de conexão: "
                    f"{error}"
                )

                if attempt < MAX_RETRIES:

                    time.sleep(3)

                    continue

                raise RuntimeError(
                    f"Falha de conexão com "
                    f"a API-Football: {error}"
                )

            except Exception as error:

                last_error = error

                if attempt < MAX_RETRIES:

                    time.sleep(3)

                    continue

                raise

        raise RuntimeError(
            f"Erro na API: {last_error}"
        )
