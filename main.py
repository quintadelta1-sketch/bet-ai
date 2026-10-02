FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 65.0
MAX_MERCADOS_TALAO = 3


def classificar(prob):
    if prob >= PROBABILIDADE_ALTA:
        return "ALTA", "🟢"

    if prob >= FILTRO_MINIMO:
        return "MEDIA", "🟡"

    return "BAIXA", "🔴"


def criar_mercados(jogo):

    mercados = []

    ajustes = {
        "goals": 4,
        "corners": 1,
        "shots": 3,
        "shots_on_target": 5,
        "tackles": 2,
        "cards": -2,
        "fouls": -1,
    }

    for nome, valores in jogo["stats"].items():

        casa = valores[0]
        fora = valores[1]

        total = casa + fora

        prob_mais = (total / (total + 5.0)) * 100

        prob_mais += ajustes.get(nome, 0)

        prob_mais = max(0, min(prob_mais, 85))

        prob_menos = 100 - prob_mais

        possibilidades = [
            ("Mais", prob_mais),
            ("Menos", prob_menos)
        ]

        for lado, prob in possibilidades:

            if prob >= FILTRO_MINIMO:

                classe, simbolo = classificar(prob)

                edge = abs(prob - 50)

                score = round(
                    (prob * 0.70) +
                    (edge * 0.30),
                    2
                )

                mercados.append({
                    "market": nome,
                    "side": lado,
                    "probability": round(prob, 2),
                    "score": score,
                    "classification": classe,
                    "symbol": simbolo
                })

    return mercados


def selecionar_mercados(mercados):

    ordenados = sorted(
        mercados,
        key=lambda x: (
            x["score"],
            x["probability"]
        ),
        reverse=True
    )

    selecionados = []

    usados = set()

    for item in ordenados:

        if item["market"] in usados:
            continue

        selecionados.append(item)

        usados.add(item["market"])

        if len(selecionados) == MAX_MERCADOS_TALAO:
            break

    return selecionados


def imprimir_jogo(jogo):

    print()
    print("=" * 50)
    print(
        f"JOGO: {jogo['home']} x "
        f"{jogo['away']}"
    )
    print("=" * 50)

    print()
    print("ESTATISTICAS")

    for nome, valores in jogo["stats"].items():

        print(
            f"{nome}: "
            f"Casa {valores[0]} | "
            f"For a {valores[1]}"
        )

    mercados = criar_mercados(jogo)

    print()
    print("PROBABILIDADES")

    for item in mercados:

        print(
            f"{item['market']}: "
            f"{item['side']} = "
            f"{item['probability']:.2f}% "
            f"[{item['symbol']} "
            f"{item['classification']}]"
        )

    selecionados = selecionar_mercados(mercados)

    print()
    print(
        "=" * 10 +
        " TALAO BET-AI V9 " +
        "=" * 10
    )

    if not selecionados:

        print(
            "Nenhum mercado "
            "passou pelo filtro."
        )

    else:

        for numero, item in enumerate(
            selecionados,
            1
        ):

            print(
                f"{numero}. "
                f"{item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%) "
                f"[{item['symbol']} "
                f"{item['classification']}]"
            )

        media = (
            sum(
                item["probability"]
                for item in selecionados
            )
            / len(selecionados)
        )

        print("-" * 50)

        print(
            f"Probabilidade media: "
            f"{media:.2f}%"
        )

    print()
    print(
        f"Filtro utilizado: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        "Observacao: estimativa do modelo, "
        "nao garantia de resultado."
    )

    selecionados_ids = {
        (
            item["market"],
            item["side"]
        )
        for item in selecionados
    }

    descartados = [
        item
        for item in mercados
        if (
            item["market"],
            item["side"]
        ) not in selecionados_ids
    ]

    print()
    print(
        "=" * 10 +
        " MERCADOS DESCARTADOS " +
        "=" * 10
    )

    if descartados:

        for item in descartados:

            print(
                f"- {item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%)"
            )

    else:

        print(
            "Nenhum mercado descartado."
        )


JOGOS = [

    {
        "home": "Flamengo",
        "away": "Palmeiras",

        "stats": {

            "goals": (1.8, 1.4),

            "corners": (6.2, 4.8),

            "shots": (14.5, 11.2),

            "shots_on_target": (5.8, 4.3),

            "tackles": (15.0, 16.2),

            "cards": (2.1, 2.5),

            "fouls": (12.4, 13.1)
        }
    },

    {
        "home": "Barcelona",
        "away": "Real Madrid",

        "stats": {

            "goals": (2.1, 1.7),

            "corners": (6.5, 5.1),

            "shots": (16.2, 12.8),

            "shots_on_target": (6.4, 5.0),

            "tackles": (13.8, 15.1),

            "cards": (1.8, 2.3),

            "fouls": (10.8, 12.7)
        }
    }
]


def main():

    print()
    print(
        "=" * 12 +
        " BET-AI V9 " +
        "=" * 12
    )

    print(
        f"Filtro minimo: "
        f"{FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Probabilidade alta: "
        f"{PROBABILIDADE_ALTA:.0f}%"
    )

    print("=" * 36)

    for jogo in JOGOS:

        imprimir_jogo(jogo)

    print()
    print("=" * 36)
    print("BET-AI V9 FINALIZADO")
    print("=" * 36)


if __name__ == "__main__":

    main()
