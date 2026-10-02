def avaliar_selecao(
    selecao,
    total_real
):

    linha = selecao["line"]

    if selecao["side"] == "Mais":

        return total_real > linha

    return total_real < linha


def resumo_backtest(registros):

    total = 0

    acertos = 0

    for registro in registros:

        resultado = registro.get(
            "result"
        )

        if resultado is None:
            continue

        for selecao in registro.get(
            "selections",
            []
        ):

            total += 1

            if avaliar_selecao(
                selecao,
                resultado
            ):

                acertos += 1

    taxa = (
        acertos / total * 100
        if total
        else 0.0
    )

    return {

        "apostas_avaliadas":
            total,

        "acertos":
            acertos,

        "erros":
            total - acertos,

        "taxa_acerto":
            round(taxa, 2)
    }
