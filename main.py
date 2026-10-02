# ============================================================
# BET-AI V11
# Sistema experimental de análise estatística de futebol
# ============================================================

FILTRO_MINIMO = 60.0
PROBABILIDADE_ALTA = 75.0
MAX_SELECOES = 3


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(probabilidade):
    if probabilidade >= PROBABILIDADE_ALTA:
        return "ALTA"
    elif probabilidade >= FILTRO_MINIMO:
        return "MEDIA"
    else:
        return "BAIXA"


# ============================================================
# CÁLCULO DE PROBABILIDADE
# ============================================================

def calcular_probabilidade(valor_casa, valor_fora):
    total = valor_casa + valor_fora

    if total <= 0:
        return 0.0, 0.0

    prob_casa = (valor_casa / total) * 100
    prob_fora = (valor_fora / total) * 100

    return round(prob_casa, 2), round(prob_fora, 2)


# ============================================================
# PONTUAÇÃO DO MERCADO
# ============================================================

def calcular_score(probabilidade, edge):
    score = (
        (probabilidade * 0.70)
        + (edge * 0.30)
    )

    return round(score, 2)


# ============================================================
# GERAR MERCADOS
# ============================================================

def gerar_mercados(estatisticas):

    mercados = []

    for mercado, valores in estatisticas.items():

        casa = valores["casa"]
        fora = valores["fora"]

        mais, menos = calcular_probabilidade(casa, fora)

        edge_mais = abs(mais - 50.0)
        edge_menos = abs(menos - 50.0)

        # ----------------------------------------------------
        # MERCADO MAIS
        # ----------------------------------------------------

        if mais >= FILTRO_MINIMO:

            mercados.append({
                "market": mercado,
                "side": "Mais",
                "probability": mais,
                "opposite": menos,
                "edge": round(edge_mais, 2),
                "score": calcular_score(mais, edge_mais),
                "classification": classificar(mais)
            })

        # ----------------------------------------------------
        # MERCADO MENOS
        # ----------------------------------------------------

        if menos >= FILTRO_MINIMO:

            mercados.append({
                "market": mercado,
                "side": "Menos",
                "probability": menos,
                "opposite": mais,
                "edge": round(edge_menos, 2),
                "score": calcular_score(menos, edge_menos),
                "classification": classificar(menos)
            })

    return mercados


# ============================================================
# SELEÇÃO INTELIGENTE
# ============================================================

def selecionar_mercados(mercados):

    # Ordena pela pontuação
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

        if len(selecionados) >= MAX_SELECOES:
            break

    return selecionados


# ============================================================
# MOSTRAR ESTATÍSTICAS
# ============================================================

def mostrar_estatisticas(estatisticas):

    print("\nESTATÍSTICAS")

    for mercado, valores in estatisticas.items():

        print(
            f"{mercado}: "
            f"Casa {valores['casa']} | "
            f"Fora {valores['fora']}"
        )


# ============================================================
# MOSTRAR PROBABILIDADES
# ============================================================

def mostrar_probabilidades(mercados):

    print("\nPROBABILIDADES")

    if not mercados:
        print("Nenhum mercado atingiu o filtro mínimo.")
        return

    for item in mercados:

        print(
            f"{item['market']}: "
            f"{item['side']} = "
            f"{item['probability']:.2f}% "
            f"[{item['classification']}]"
        )


# ============================================================
# MOSTRAR TALÃO
# ============================================================

def mostrar_talao(selecionados):

    print("\n========== TALÃO BET-AI V11 ==========")

    if not selecionados:

        print("Nenhum mercado atingiu o filtro mínimo.")
        print("--------------------------------------")
        print("Probabilidade média: 0.00%")
        print(f"Filtro utilizado: {FILTRO_MINIMO:.0f}%")
        print(f"Máximo de seleções: {MAX_SELECOES}")
        return

    for numero, item in enumerate(selecionados, start=1):

        print(
            f"{numero}. "
            f"{item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )

    probabilidade_media = (
        sum(item["probability"] for item in selecionados)
        / len(selecionados)
    )

    print("--------------------------------------")
    print(
        f"Probabilidade média: "
        f"{probabilidade_media:.2f}%"
    )
    print(f"Filtro utilizado: {FILTRO_MINIMO:.0f}%")
    print(f"Máximo de seleções: {MAX_SELECOES}")


# ============================================================
# MOSTRAR DESCARTADOS
# ============================================================

def mostrar_descartados(mercados, selecionados):

    print("\n========== MERCADOS DESCARTADOS ==========")

    selecionados_ids = {
        (item["market"], item["side"])
        for item in selecionados
    }

    descartados = []

    for item in mercados:

        identificador = (
            item["market"],
            item["side"]
        )

        if identificador not in selecionados_ids:
            descartados.append(item)

    if not descartados:

        print("Nenhum mercado descartado.")
        return

    for item in descartados:

        print(
            f"- {item['market']} - "
            f"{item['side']} "
            f"({item['probability']:.2f}%) "
            f"[{item['classification']}]"
        )


# ============================================================
# ANALISAR JOGO
# ============================================================

def analisar_jogo(nome_jogo, estatisticas):

    print("\n")
    print("==========================================")
    print(f"JOGO: {nome_jogo}")
    print("==========================================")

    mostrar_estatisticas(estatisticas)

    mercados = gerar_mercados(estatisticas)

    mostrar_probabilidades(mercados)

    selecionados = selecionar_mercados(mercados)

    mostrar_talao(selecionados)

    mostrar_descartados(
        mercados,
        selecionados
    )

    print("\nObservação:")
    print(
        "As probabilidades são estimativas "
        "experimentais do modelo e não garantem "
        "o resultado de uma aposta."
    )

    return selecionados


# ============================================================
# MAIN
# ============================================================

def main():

    print("==========================================")
    print("          BET-AI V11")
    print("==========================================")

    print(
        f"Filtro mínimo: {FILTRO_MINIMO:.0f}%"
    )

    print(
        f"Probabilidade alta: "
        f"{PROBABILIDADE_ALTA:.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )

    print("==========================================")

    # ========================================================
    # JOGO 1
    # ========================================================

    flamengo_palmeiras = {

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
            "casa": 12.4,
            "fora": 13.1
        }
    }

    analisar_jogo(
        "Flamengo x Palmeiras",
        flamengo_palmeiras
    )

    # ========================================================
    # JOGO 2
    # ========================================================

    barcelona_real = {

        "goals": {
            "casa": 2.1,
            "fora": 1.7
        },

        "corners": {
            "casa": 6.5,
            "fora": 5.1
        },

        "shots": {
            "casa": 16.2,
            "fora": 12.8
        },

        "shots_on_target": {
            "casa": 6.4,
            "fora": 5.0
        },

        "tackles": {
            "casa": 13.8,
            "fora": 15.1
        },

        "cards": {
            "casa": 1.8,
            "fora": 2.3
        },

        "fouls": {
            "casa": 10.8,
            "fora": 12.7
        }
    }

    analisar_jogo(
        "Barcelona x Real Madrid",
        barcelona_real
    )

    print("\n==========================================")
    print("        BET-AI V11 FINALIZADO")
    print("==========================================")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
