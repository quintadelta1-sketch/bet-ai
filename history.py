import json

from pathlib import Path
from datetime import datetime, timezone


HISTORY_FILE = Path(
    "data/history.json"
)


def salvar_analise(
    nome_jogo,
    selecionados
):

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if HISTORY_FILE.exists():

        try:

            historico = json.loads(
                HISTORY_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError:

            historico = []

    else:

        historico = []

    registro = {

        "timestamp_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "game": nome_jogo,

        "selections":
            selecionados,

        "status":
            "pending"
    }

    historico.append(
        registro
    )

    HISTORY_FILE.write_text(

        json.dumps(
            historico,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"
    )
