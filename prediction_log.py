import json
import os
from datetime import datetime


ARQUIVO = "data/predictions.json"


def registrar_previsoes(jogo, selecionados):

    os.makedirs("data", exist_ok=True)

    registros = []

    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)

            if not isinstance(registros, list):
                registros = []

        except Exception:
            registros = []

    agora = datetime.utcnow().isoformat() + "Z"

    for mercado in selecionados:

        registro = {
            "id": len(registros) + 1,
            "data": agora,
            "home": jogo.get("home", ""),
            "away": jogo.get("away", ""),
            "mercado": mercado["mercado"],
            "linha": mercado["linha"],
            "probabilidade": mercado["probabilidade"],
            "resultado": None
        }

        registros.append(registro)

    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(
            registros,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    return registros
