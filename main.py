from statistics import mean


# ============================================================
# BET-AI V14
# Sistema experimental de análise estatística de partidas
# ============================================================

VERSAO = "14.0"

FILTRO_MINIMO = 0.60
MAX_SELECOES = 3


# ============================================================
# DADOS DE EXEMPLO
# ============================================================

GAME = {
    "home": "Casa FC",
    "away": "Fora FC",

    "goals_home": 1.8,
    "goals_away": 1.4,

    "corners_home": 6.2,
    "corners_away": 4.8,

    "shots_home": 14.5,
    "shots_away": 11.2,

    "shots_on_target_home": 5.8,
    "shots_on_target_away": 4.3,

    "tackles_home": 15.0,
    "tackles_away": 16.2,

    "cards_home": 2.1,
    "cards_away": 2.5,

    "fouls_home": 12.4,
    "fouls_away": 13.1,
}


# ============================================================
# HISTÓRICO PARA BACKTEST
# ============================================================

HISTORICO = [
    {
        "market": "goals",
        "line": 2.5,
        "probability": 0.68,
        "result": "over",
    },
    {
        "market": "shots",
        "line": 24.5,
        "probability": 0.72,
        "result": "over",
    },
    {
        "market": "corners",
        "line": 9.5,
        "probability": 0.66,
        "result": "under",
    },
    {
        "market": "shots_on_target",
        "line": 8.5,
        "probability": 0.74,
        "result": "over",
    },
    {
        "market": "tackles",
        "line": 30.5,
        "probability": 0.63,
        "result": "under",
    },
    {
        "market": "cards",
        "line": 4.5,
        "probability": 0.61,
        "result": "under",
    },
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(value, maximum))


def percentual(valor):
    return round(valor * 100, 2)


def classificacao(probabilidade):
    if probabilidade >= 0.75:
        return "ALTA"
    elif probabilidade >= 0.60:
        return "MEDIA"
    return "BAIXA"


def validar_game(game):
    campos = [
        "home",
        "away",
        "goals_home",
        "goals_away",
        "corners_home",
        "corners_away",
        "shots_home",
        "shots_away",
        "shots_on_target_home",
        "shots_on_target_away",
        "tackles_home",
        "tackles_away",
        "cards_home",
        "cards_away",
        "fouls_home",
        "fouls_away",
    ]

    faltando = [campo for campo in campos if campo not in game]

    if faltando:
        raise ValueError(
            "Campos ausentes: " + ", ".join(faltando)
        )

    return True


# ============================================================
# CÁLCULO DE PROBABILIDADES
# ============================================================

def calcular_probabilidade(valor, linha, margem=0.15):
    if linha <= 0:
        return 0.0

    diferenca = (valor - linha) / linha

    probabilidade = 0.50 + (diferenca / margem) * 0.25

    return clamp(probabilidade, 0.05, 0.95)


def analisar_mercado(nome, valor, linha):
    over = calcular_probabilidade(valor, linha)

    # Probabilidade complementar experimental
    under = clamp(1.0 - over)

    mercados = []

    mercados.append({
        "market": nome,
        "side": "Mais",
        "line": linha,
        "probability": over,
        "opposite": under,
        "classification": classificacao(over),
    })

    mercados.append({
        "market": nome,
        "side": "Menos",
        "line": linha,
        "probability": under,
        "opposite": over,
        "classification": classificacao(under),
    })

    return mercados


# ============================================================
# CONSTRUÇÃO DOS MERCADOS
# ============================================================

def gerar_mercados(game):

    mercados = []

    # GOLS
    total_goals = game["goals_home"] + game["goals_away"]

    mercados.extend(
        analisar_mercado(
            "gols",
            total_goals,
            2.5
        )
    )

    # ESCANTEIOS
    total_corners = (
        game["corners_home"] +
        game["corners_away"]
    )

    mercados.extend(
        analisar_mercado(
            "corners",
            total_corners,
            9.5
        )
    )

    # FINALIZAÇÕES
    total_shots = (
        game["shots_home"] +
        game["shots_away"]
    )

    mercados.extend(
        analisar_mercado(
            "shots",
            total_shots,
            24.5
        )
    )

    # FINALIZAÇÕES NO ALVO
    total_shots_on_target = (
        game["shots_on_target_home"] +
        game["shots_on_target_away"]
    )

    mercados.extend(
        analisar_mercado(
            "shots_on_target",
            total_shots_on_target,
            8.5
        )
    )

    # DESARMES
    total_tackles = (
        game["tackles_home"] +
        game["tackles_away"]
    )

    mercados.extend(
        analisar_mercado(
            "tackles",
            total_tackles,
            30.5
        )
    )

    # CARTÕES
    total_cards = (
        game["cards_home"] +
        game["cards_away"]
    )

    mercados.extend(
        analisar_mercado(
            "cards",
            total_cards,
            4.5
        )
    )

    # FALTAS
    total_fouls = (
        game["fouls_home"] +
        game["fouls_away"]
    )

    mercados.extend(
        analisar_mercado(
            "faltas",
            total_fouls,
            25.5
        )
    )

    return mercados


# ============================================================
# SELEÇÃO DOS MERCADOS
# ============================================================

def selecionar_mercados(mercados):

    elegiveis = [
        item
        for item in mercados
        if item["probability"] >= FILTRO_MINIMO
    ]

    elegiveis.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    selecionados = []
    mercados_usados = set()

    for item in elegiveis:

        if item["market"] in mercados_usados:
            continue

        selecionados.append(item)
        mercados_usados.add(item["market"])

        if len(selecionados) >= MAX_SELECOES:
            break

    return selecionados


# ============================================================
# BACKTEST
# ============================================================

def executar_backtest(historico):

    total = len(historico)
    acertos = 0
    erros = 0

    for item in historico:

        probabilidade = item.get("probability", 0)
        resultado = item.get("result")

        # Simulação experimental:
        # mercados com probabilidade >= 60%
        # são considerados previsões positivas.
        previsao = probabilidade >= FILTRO_MINIMO

        resultado_real = resultado in (
            "over",
            "under"
        )

        if previsao and resultado_real:
            acertos += 1
        else:
            erros += 1

    if total > 0:
        taxa = acertos / total
    else:
        taxa = 0.0

    return {
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "taxa": taxa,
    }


# ============================================================
# RELATÓRIO
# ============================================================

def imprimir_estatisticas(game):

    print()
    print("========== BET-AI V14 ==========")
    print()
    print(
        f"PARTIDA: {game['home']} x {game['away']}"
    )

    print()
    print("========== ESTATISTICAS ==========")

    print(
        f"gols: Casa {game['goals_home']} | "
        f"Fora {game['goals_away']}"
    )

    print(
        f"corners: Casa {game['corners_home']} | "
        f"Fora {game['corners_away']}"
    )

    print(
        f"shots: Casa {game['shots_home']} | "
        f"Fora {game['shots_away']}"
    )

    print(
        f"shots_on_target: Casa "
        f"{game['shots_on_target_home']} | "
        f"Fora {game['shots_on_target_away']}"
    )

    print(
        f"tackles: Casa {game['tackles_home']} | "
        f"Fora {game['tackles_away']}"
    )

    print(
        f"cards: Casa {game['cards_home']} | "
        f"Fora {game['cards_away']}"
    )

    print(
        f"faltas: Casa {game['fouls_home']} | "
        f"Fora {game['fouls_away']}"
    )


def imprimir_probabilidades(mercados):

    print()
    print("========== PROBABILIDADES ==========")

    for item in mercados:

        prob = percentual(item["probability"])

        print(
            f"{item['market']} - "
            f"{item['side']} {item['line']} = "
            f"{prob:.2f}% "
            f"[{item['classification']}]"
        )


def imprimir_talao(selecionados):

    print()
    print("========== TALAO BET-AI V14 ==========")

    if not selecionados:
        print(
            "Nenhum mercado atingiu o filtro mínimo."
        )
        return

    probabilidades = []

    for indice, item in enumerate(
        selecionados,
        start=1
    ):

        prob = percentual(item["probability"])
        probabilidades.append(
            item["probability"]
        )

        print(
            f"{indice}. "
            f"{item['market']} - "
            f"{item['side']} {item['line']} "
            f"({prob:.2f}%) "
            f"[{item['classification']}]"
        )

    media = mean(probabilidades)

    print()
    print(
        f"Probabilidade média: "
        f"{percentual(media):.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{percentual(FILTRO_MINIMO):.0f}%"
    )

    print(
        f"Máximo de seleções: {MAX_SELECOES}"
    )


def imprimir_descartados(
    mercados,
    selecionados
):

    selecionados_ids = {
        (
            item["market"],
            item["side"],
            item["line"]
        )
        for item in selecionados
    }

    descartados = [
        item
        for item in mercados
        if (
            item["market"],
            item["side"],
            item["line"]
        ) not in selecionados_ids
    ]

    print()
    print("========== MERCADOS DESCARTADOS ==========")

    if not descartados:
        print("Nenhum mercado descartado.")
        return

    for item in descartados:

        prob = percentual(item["probability"])

        print(
            f"- {item['market']} - "
            f"{item['side']} {item['line']} "
            f"({prob:.2f}%) "
            f"[{item['classification']}]"
        )


def imprimir_backtest(resultado):

    print()
    print("========== BACKTEST ==========")

    print(
        f"Total avaliado: "
        f"{resultado['total']}"
    )

    print(
        f"Acertos: "
        f"{resultado['acertos']}"
    )

    print(
        f"Erros: "
        f"{resultado['erros']}"
    )

    print(
        f"Taxa de acerto: "
        f"{percentual(resultado['taxa']):.2f}%"
    )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():

    validar_game(GAME)

    imprimir_estatisticas(GAME)

    mercados = gerar_mercados(GAME)

    imprimir_probabilidades(mercados)

    selecionados = selecionar_mercados(
        mercados
    )

    imprimir_talao(selecionados)

    imprimir_descartados(
        mercados,
        selecionados
    )

    backtest = executar_backtest(
        HISTORICO
    )

    imprimir_backtest(backtest)

    print()
    print("========================================")
    print("OBSERVAÇÃO:")
    print(
        "As probabilidades são estimativas "
        "experimentais do modelo."
    )
    print(
        "Não representam garantia de resultado."
    )
    print("========================================")

    print()
    print(
        "========== BET-AI V14 FINALIZADO =========="
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
