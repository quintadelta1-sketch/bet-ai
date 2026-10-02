# ============================================
# BET-AI V9
# Analisador estatístico de mercados
# ============================================

FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 65.0
MAX_MERCADOS_TALAO = 3


# --------------------------------------------
# CLASSIFICAÇÃO
# --------------------------------------------

def classificar(probabilidade):
    if probabilidade >= PROBABILIDADE_ALTA:
        return "ALTA", "🟢"

    if probabilidade >= FILTRO_MINIMO:
        return "MÉDIA", "🟡"

    return "BAIXA", "🔴"


# --------------------------------------------
# PONTUAÇÃO DO MODELO
# --------------------------------------------

def calcular_score(probabilidade, edge):
    score = (
        (probabilidade * 0.70)
        + (edge * 0.30)
    )

    return round(score, 2)


# --------------------------------------------
# CRIAÇÃO DOS MERCADOS
# --------------------------------------------

def criar_mercados(jogo):

    mercados = []

    estatisticas = jogo["stats"]

    for mercado, dados in estatisticas.items():

        casa = dados["casa"]
        fora = dados["fora"]

        total = casa + fora

        if total <= 0:
            continue

        # Estimativa simples baseada na participação
        # do mandante e visitante no total.
        prob_mais = (total / (total + 5.0)) * 100

        # Ajuste para evitar probabilidades artificiais
        if prob_mais > 85:
            prob_mais = 85

        if prob_mais < 40:
            prob_mais = 40

        prob_menos = 100 - prob_mais

        # Pequeno ajuste específico por mercado
        if mercado == "goals":
            prob_mais += 4

        elif mercado == "shots":
            prob_mais += 3

        elif mercado == "shots_on_target":
            prob_mais += 5

        elif mercado == "corners":
            prob_mais += 1

        elif mercado == "tackles":
            prob_mais += 2

        elif mercado == "cards":
            prob_mais -= 2

        elif mercado == "fouls":
            prob_mais -= 1

        # Limites
        prob_mais = max(0, min(prob_mais, 85))
        prob_menos = 100 - prob_mais

        # EDGE
        edge_mais = abs(prob_mais - 50)
        edge_menos = abs(prob_menos - 50)

        # ------------------------------------
        # MERCADO MAIS
        # ------------------------------------

        if prob_mais >= FILTRO_MINIMO:

            classificacao, simbolo = classificar(prob_mais)

            score = calcular_score(
                prob_mais,
                edge_mais
            )

            mercados.append({
                "market": mercado,
                "side": "Mais",
                "probability": round(prob_mais, 2),
                "opposite": round(prob_menos, 2),
                "edge": round(edge_mais, 2),
                "score": score,
                "classification": classificacao,
                "symbol": simbolo
            })

        # ------------------------------------
        # MERCADO MENOS
        # ------------------------------------

        if prob_menos >= FILTRO_MINIMO:

            classificacao, simbolo = classificar(prob_menos)

            score = calcular_score(
                prob_menos,
                edge_menos
            )

            mercados.append({
                "market": mercado,
                "side": "Menos",
                "probability": round(prob_menos, 2),
                "opposite": round(prob_mais, 2),
                "edge": round(edge_menos, 2),
                "score": score,
                "classification": classificacao,
                "symbol": simbolo
            })

    return mercados


# --------------------------------------------
# SELEÇÃO DOS MERCADOS
# --------------------------------------------

def selecionar_mercados(mercados):

    mercados = sorted(
        mercados,
        key=lambda x: (
            x["score"],
            x["probability"]
        ),
        reverse=True
    )

    selecionados = []
    mercados_usados = set()

    for item in mercados:

        mercado = item["market"]

        # Evita repetir o mesmo mercado
        if mercado in mercados_usados:
            continue

        selecionados.append(item)
        mercados_usados.add(mercado)

        if len(selecionados) >= MAX_MERCADOS_TALAO:
            break

    return selecionados


# --------------------------------------------
# IMPRESSÃO DO JOGO
# --------------------------------------------

def imprimir_jogo(jogo):

    print()
    print("=" * 48)
    print(f"JOGO: {jogo['home']} x {jogo['away']}")
    print("=" * 48)

    print()
    print("ESTATÍSTICAS")

    for mercado, dados in jogo["stats"].items():

        print(
            f"{mercado}: "
            f"Casa {dados['casa']} | "
            f"Fora {dados['fora']}"
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
    print("=" * 14 + " TALÃO BET-AI V9 " + "=" * 14)

    if not selecionados:

        print("Nenhum mercado passou pelo filtro.")

    else:

        for numero, item in enumerate(
            selecionados,
            start=1
        ):

            print(
                f"{numero}. "
                f"{item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%) "
                f"[{item['symbol']} "
                f"{item['classification']}]"
            )

        probabilidade_media = (
            sum(
                item["probability"]
                for item in selecionados
            )
            / len(selecionados)
        )

        print()
        print(
            f"Probabilidade média: "
            f"{probabilidade_media:.2f}%"
        )

    print()
    print(f"Filtro utilizado: {FILTRO_MINIMO:.0f}%")

    print(
        "Observação: as probabilidades são "
        "estimativas do modelo e não representam "
        "garantia de resultado."
    )

    # ----------------------------------------
    # MERCADOS DESCARTADOS
    # ----------------------------------------

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
    print("=" * 14 + " MERCADOS DESCARTADOS " + "=" * 14)

    if not descartados:

        print("Nenhum mercado descartado.")

    else:

        for item in descartados:

            print(
                f"- {item['market']} - "
                f"{item['side']} "
                f"({item['probability']:.2f}%) "
                f"[abaixo da seleção]"
            )


# --------------------------------------------
# DADOS DE TESTE
# --------------------------------------------

JOGOS = [

    {
        "home": "Flamengo",
        "away": "Palmeiras",

        "stats": {

            "goals": {
                "casa": 1.8,
                "fora": 1.4
            },

            "corners": {
                "casa": 6.2,
                "fora": 4.8
            },

            "shots": {
                "casa": 14.5,
                "fora": 11.2
            },

            "shots_on_target": {
                "casa": 5.8,
                "fora": 4.3
            },

            "tackles": {
                "casa": 15.0,
                "fora": 16.2
            },

            "cards": {
                "casa": 2.1,
                "fora": 2.5
            },

            "fouls": {
