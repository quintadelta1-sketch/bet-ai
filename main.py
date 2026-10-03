from statistics import mean


# ============================================================
# BET-AI V15
# Sistema experimental de análise estatística de futebol
# ============================================================

VERSAO = "V15"

FILTRO_MINIMO = 0.60
MAX_SELECOES = 3


# ============================================================
# UTILIDADES
# ============================================================

def limitar(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, valor))


def percentual(valor):
    return round(valor * 100, 2)


def classificacao(probabilidade):
    if probabilidade >= 0.80:
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

    for campo in campos[2:]:
        if not isinstance(game[campo], (int, float)):
            raise ValueError(
                f"O campo '{campo}' precisa ser numérico."
            )

        if game[campo] < 0:
            raise ValueError(
                f"O campo '{campo}' não pode ser negativo."
            )

    return True


# ============================================================
# CÁLCULO DAS ESTATÍSTICAS
# ============================================================

def estatisticas_jogo(game):

    return {
        "goals": (
            game["goals_home"],
            game["goals_away"]
        ),

        "corners": (
            game["corners_home"],
            game["corners_away"]
        ),

        "shots": (
            game["shots_home"],
            game["shots_away"]
        ),

        "shots_on_target": (
            game["shots_on_target_home"],
            game["shots_on_target_away"]
        ),

        "tackles": (
            game["tackles_home"],
            game["tackles_away"]
        ),

        "cards": (
            game["cards_home"],
            game["cards_away"]
        ),

        "faltas": (
            game["fouls_home"],
            game["fouls_away"]
        ),
    }


def media_total(valores):
    return mean(valores)


# ============================================================
# MODELO DE PROBABILIDADE
# ============================================================

def calcular_probabilidade(total, linha, lado):

    if lado == "Mais":

        if total <= linha:
            prob = 0.50
        else:
            diferenca = total - linha
            prob = 0.50 + (diferenca / max(linha, 1)) * 0.50

    else:

        if total >= linha:
            prob = 0.50
        else:
            diferenca = linha - total
            prob = 0.50 + (diferenca / max(linha, 1)) * 0.50

    return limitar(prob)


def calcular_score(probabilidade):

    score = (
        probabilidade * 0.70
        + classificacao_pontuacao(probabilidade) * 0.30
    )

    return round(score, 4)


def classificacao_pontuacao(probabilidade):

    if probabilidade >= 0.80:
        return 1.0

    if probabilidade >= 0.60:
        return 0.70

    return 0.40


# ============================================================
# ANÁLISE DE UM MERCADO
# ============================================================

def analisar_mercado(
    mercado,
    total,
    linha,
    lado
):

    probabilidade = calcular_probabilidade(
        total,
        linha,
        lado
    )

    classificacao_atual = classificacao(
        probabilidade
    )

    score = calcular_score(
        probabilidade
    )

    return {
        "market": mercado,
        "line": linha,
        "side": lado,
        "probability": round(probabilidade, 4),
        "score": score,
        "classification": classificacao_atual,
    }


# ============================================================
# GERAÇÃO DOS MERCADOS
# ============================================================

def gerar_mercados(game):

    stats = estatisticas_jogo(game)

    mercados = []

    linhas = {
        "goals": 2.5,
        "corners": 9.5,
        "shots": 24.5,
        "shots_on_target": 8.5,
        "tackles": 30.5,
        "cards": 4.5,
        "faltas": 25.5,
    }

    for mercado, valores in stats.items():

        total = media_total(valores)

        linha = linhas[mercado]

        mais = analisar_mercado(
            mercado,
            total,
            linha,
            "Mais"
        )

        menos = analisar_mercado(
            mercado,
            total,
            linha,
            "Menos"
        )

        mercados.append(mais)
        mercados.append(menos)

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

    elegiveis = sorted(
        elegiveis,
        key=lambda x: (
            x["score"],
            x["probability"]
        ),
        reverse=True
    )

    selecionados = []

    usados = set()

    for item in elegiveis:

        mercado = item["market"]

        if mercado in usados:
            continue

        selecionados.append(item)

        usados.add(mercado)

        if len(selecionados) >= MAX_SELECOES:
            break

    return selecionados


# ============================================================
# MERCADOS DESCARTADOS
# ============================================================

def mercados_descartados(mercados, selecionados):

    selecionados_ids = {
        (
            item["market"],
            item["side"],
            item["line"]
        )
        for item in selecionados
    }

    descartados = []

    for item in mercados:

        identificador = (
            item["market"],
            item["side"],
            item["line"]
        )

        if identificador not in selecionados_ids:
            descartados.append(item)

    descartados.sort(
        key=lambda x: x["probability"],
        reverse=True
    )

    return descartados


# ============================================================
# RELATÓRIO
# ============================================================

def imprimir_estatisticas(game):

    print()
    print("========== ESTATISTICAS ==========")

    print(
        f"goals: Casa {game['goals_home']} | "
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

        print(
            f"{item['market']} - "
            f"{item['side']} {item['line']} = "
            f"{percentual(item['probability']):.2f}% "
            f"[{item['classification']}]"
        )


def imprimir_talao(selecionados):

    print()
    print(
        f"========== TALAO BET-AI {VERSAO} =========="
    )

    if not selecionados:

        print(
            "Nenhum mercado atingiu o filtro mínimo."
        )

        return

    for indice, item in enumerate(
        selecionados,
        start=1
    ):

        print(
            f"{indice}. "
            f"{item['market']} - "
            f"{item['side']} {item['line']} "
            f"("
            f"{percentual(item['probability']):.2f}%"
            f") "
            f"[{item['classification']}]"
        )

    media = mean(
        item["probability"]
        for item in selecionados
    )

    print("------------------------------------")

    print(
        f"Probabilidade média: "
        f"{percentual(media):.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{percentual(FILTRO_MINIMO):.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )


def imprimir_descartados(descartados):

    print()
    print("========== MERCADOS DESCARTADOS ==========")

    if not descartados:

        print(
            "Nenhum mercado descartado."
        )

        return

    for item in descartados:

        print(
            f"- {item['market']} - "
            f"{item['side']} {item['line']} "
            f"("
            f"{percentual(item['probability']):.2f}%"
            f") "
            f"[{item['classification']}]"
        )


# ============================================================
# BACKTEST
# ============================================================

def executar_backtest(historico):

    total = 0
    acertos = 0
    erros = 0

    for partida in historico:

        mercados = gerar_mercados(
            partida
        )

        selecionados = selecionar_mercados(
            mercados
        )

        for item in selecionados:

            total += 1

            resultado = partida.get(
                "resultado",
                {}
            )

            chave = item["market"]

            valor_real = resultado.get(
                chave
            )

            if valor_real is None:
                continue

            linha = item["line"]

            if item["side"] == "Mais":

                acertou = valor_real > linha

            else:

                acertou = valor_real < linha

            if acertou:
                acertos += 1
            else:
                erros += 1

    if total == 0:

        taxa = 0.0

    else:

        taxa = (
            acertos / total
        ) * 100

    print()
    print("========== BACKTEST ==========")

    print(
        f"Total avaliado: {total}"
    )

    print(
        f"Acertos: {acertos}"
    )

    print(
        f"Erros: {erros}"
    )

    print(
        f"Taxa de acerto: {taxa:.2f}%"
    )

    return {
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "taxa": round(taxa, 2),
    }


# ============================================================
# PARTIDA DE TESTE
# ============================================================

GAME_TESTE = {

    "home": "Casa",
    "away": "Fora",

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

    "resultado": {
        "goals": 3,
        "corners": 11,
        "shots": 27,
        "shots_on_target": 10,
        "tackles": 31,
        "cards": 5,
        "faltas": 26,
    },
}


# ============================================================
# HISTÓRICO PARA TESTE
# ============================================================

HISTORICO_TESTE = [

    GAME_TESTE,

    {
        **GAME_TESTE,
        "goals_home": 2.0,
        "goals_away": 1.2,
        "shots_home": 16.0,
        "shots_away": 12.0,
        "resultado": {
            "goals": 3,
            "corners": 10,
            "shots": 29,
            "shots_on_target": 10,
            "tackles": 32,
            "cards": 5,
            "faltas": 27,
        },
    },

    {
        **GAME_TESTE,
        "goals_home": 1.9,
        "goals_away": 1.5,
        "shots_home": 15.0,
        "shots_away": 12.0,
        "resultado": {
            "goals": 4,
            "corners": 12,
            "shots": 28,
            "shots_on_target": 11,
            "tackles": 33,
            "cards": 6,
            "faltas": 28,
        },
    },
]


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 50)
    print(f"BET-AI {VERSAO}")
    print("=" * 50)

    try:

        validar_game(
            GAME_TESTE
        )

        imprimir_estatisticas(
            GAME_TESTE
        )

        mercados = gerar_mercados(
            GAME_TESTE
        )

        imprimir_probabilidades(
            mercados
        )

        selecionados = selecionar_mercados(
            mercados
        )

        imprimir_talao(
            selecionados
        )

        descartados = mercados_descartados(
            mercados,
            selecionados
        )

        imprimir_descartados(
            descartados
        )

        executar_backtest(
            HISTORICO_TESTE
        )

        print()
        print("=" * 50)
        print("OBSERVAÇÃO:")
        print(
            "As probabilidades são estimativas "
            "experimentais do modelo."
        )
        print(
            "Não representam garantia de resultado."
        )
        print("=" * 50)

        print()
        print("=" * 50)
        print(f"BET-AI {VERSAO} FINALIZADO")
        print("=" * 50)

    except Exception as erro:

        print()
        print("========== ERRO ==========")
        print(
            f"{type(erro).__name__}: {erro}"
        )
        raise


if __name__ == "__main__":
    main()
