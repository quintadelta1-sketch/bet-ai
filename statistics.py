import math


def poisson_probability(k, media):
    if media < 0:
        raise ValueError("A média não pode ser negativa.")

    if media == 0:
        return 1.0 if k == 0 else 0.0

    return (
        math.exp(-media)
        * (media ** k)
        / math.factorial(k)
    )


def poisson_cdf(k, media):
    if k < 0:
        return 0.0

    resultado = 0.0

    for i in range(k + 1):
        resultado += poisson_probability(i, media)

    return resultado


def over_under_probability(media, linha):
    if media <= 0:
        return 0.0, 100.0

    limite = math.floor(linha)

    prob_menos = poisson_cdf(
        limite,
        media
    )

    prob_mais = 1.0 - prob_menos

    return (
        round(prob_mais * 100, 2),
        round(prob_menos * 100, 2)
    )


def media_total(valor):
    return round(
        float(valor["casa"])
        + float(valor["fora"]),
        2
    )
