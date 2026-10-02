import json

from pathlib import Path

from config import (
    FILTRO_MINIMO,
    PROBABILIDADE_ALTA,
    MAX_SELECOES
)

from analyzer import gerar_mercados

from selector import (
    selecionar_mercados,
    mercados_descartados
)

from history import salvar_analise


DATA_FILE = Path(
    "data/games.json"
)


def carregar_jogos():

    with DATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as arquivo:

        dados = json.load(
            arquivo
        )

    if not isinstance(
        dados,
        list
    ):

        raise ValueError(
            "data/games.json precisa "
            "conter uma lista de jogos."
        )

    return dados


def mostrar_estatisticas(
    estatisticas
):

    print("\nESTATÍSTICAS")

    for mercado, valores in (
        estatisticas.items()
    ):

        total = (
            valores["casa"]
            + valores["fora"]
        )

        print(
            f"{mercado}: "
            f"Casa {valores['casa']} | "
            f"Fora {valores['fora']} | "
            f"Total {total:.2f}"
        )


def mostrar_probabilidades(
    mercados
):

    print(
        "\nPROBABILIDADES"
    )

    if not mercados:

        print(
            "Nenhum mercado encontrado."
        )

        return

    for item in mercados:

        print(

            f"{item['market']}: "
            f"{item['side']} "
            f"{item['line']} = "
            f"{item['probability']:.2f}% "
            f"[{item['classification']}]"

        )


def mostrar_talao(
    selecionados
):

    print(
        "\n========== "
        "TALÃO BET-AI V12 "
        "=========="
    )

    if not selecionados:

        print(
            "Nenhum mercado atingiu "
            "o filtro mínimo."
        )

        print(
            f"Filtro: "
            f"{FILTRO_MINIMO:.0f}%"
        )

        print(
            f"Máximo de seleções: "
            f"{MAX_SELECOES}"
        )

        return


    for numero, item in enumerate(
        selecionados,
        1
    ):

        print(

            f"{numero}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"{item['line']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"

        )


    media = (

        sum(
            item["probability"]
            for item in selecionados
        )

        / len(selecionados)

    )


    print(
        "--------------------------------------"
    )

    print(
        f"Probabilidade média estimada: "
        f"{media:.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )


def mostrar_descartados(
    descartados
):

    print(
        "\n========== "
        "MERCADOS DESCARTADOS "
        "=========="
    )

    if not descartados:

        print(
            "Nenhum mercado descartado."
        )

        return


    for item in descartados:

        print(

            f"- {item['market']} - "
            f"{item['side']} "
            f"{item['line']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"

        )


def analisar_jogo(
    jogo
):

    nome = jogo["game"]

    estatisticas = (
        jogo["statistics"]
    )


    print(
        "\n=========================================="
    )

    print(
        f"JOGO: {nome}"
    )

    print(
        "=========================================="
    )


    mostrar_estatisticas(
        estatisticas
    )


    mercados = gerar_mercados(
        estatisticas
    )


    mostrar_probabilidades(
        mercados
    )


    selecionados = (
        selecionar_mercados(
            mercados
        )
    )


    descartados = (
        mercados_descartados(
            mercados,
            selecionados
        )
    )


    mostrar_talao(
        selecionados
    )


    mostrar_descartados(
        descartados
    )


    salvar_analise(
        nome,
        selecionados
    )


    print(
        "\nObservação:"
    )

    print(
        "As probabilidades são "
        "estimativas experimentais "
        "do modelo."
    )

    print(
        "Não são garantia de resultado."
    )


def main():

    print(
        "=========================================="
    )

    print(
        "              BET-AI V12"
    )

    print(
        "=========================================="
    )

    print(
        f"Filtro mínimo: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Probabilidade alta: "
        f"{PROBABILIDADE_ALTA:.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )

    print(
        "=========================================="
    )


    jogos = carregar_jogos()


    for jogo in jogos:

        analisar_jogo(
            jogo
        )


    print(
        "\n=========================================="
    )

    print(
        "           BET-AI V12 FINALIZADO"
    )

    print(
        "=========================================="
    )


if __name__ == "__main__":

    main()
