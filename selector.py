from config import (
    FILTRO_MINIMO,
    MAX_SELECOES
)


def selecionar_mercados(mercados):

    elegiveis = [
        item
        for item in mercados
        if item["probability"] >= FILTRO_MINIMO
    ]

    ordenados = sorted(
        elegiveis,
        key=lambda item: (
            item["score"],
            item["probability"]
        ),
        reverse=True
    )

    selecionados = []

    usados = set()

    for item in ordenados:

        mercado = item["market"]

        if mercado in usados:
            continue

        selecionados.append(item)

        usados.add(mercado)

        if len(selecionados) >= MAX_SELECOES:
            break

    return selecionados


def mercados_descartados(
    mercados,
    selecionados
):

    ids = {
        (
            item["market"],
            item["side"]
        )
        for item in selecionados
    }

    return [
        item
        for item in mercados
        if (
            item["market"],
            item["side"]
        ) not in ids
    ]
