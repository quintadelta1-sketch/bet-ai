from config import (
    FILTRO_MINIMO,
    PROBABILIDADE_ALTA,
    LINHAS
)

from statistics import (
    media_total,
    over_under_probability
)


def classificacao(probabilidade):

    if probabilidade >= PROBABILIDADE_ALTA:
        return "ALTA"

    if probabilidade >= FILTRO_MINIMO:
        return "MEDIA"

    return "BAIXA"


def gerar_mercados(estatisticas):

    mercados = []

    for mercado, valores in estatisticas.items():

        if mercado not in LINHAS:
            continue

        media = media_total(valores)

        linha = LINHAS[mercado]

        mais, menos = over_under_probability(
            media,
            linha
        )

        opcoes = [
            ("Mais", mais, menos),
            ("Menos", menos, mais)
        ]

        for lado, probabilidade, oposta in opcoes:

            item = {
                "market": mercado,
                "side": lado,
                "line": linha,
                "mean": media,
                "probability": probabilidade,
                "opposite": oposta,
                "edge": round(
                    abs(probabilidade - 50.0),
                    2
                ),
                "score": round(
                    probabilidade,
                    2
                ),
                "classification": classificacao(
                    probabilidade
                )
            }

            mercados.append(item)

    return mercados
