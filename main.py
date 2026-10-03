import json
import os
from statistics import mean

from prediction_log import registrar_previsoes


# ============================================================
# BET-AI FINAL 1.1
# Motor de análise + seleção + registro + backtest
# ============================================================

FILTRO_MINIMO = 60.0
MAX_SELECOES = 3


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def nivel(probabilidade):
    if probabilidade >= 75:
        return "ALTA"
    elif probabilidade >= 60:
        return "MEDIA"
    return "BAIXA"


# ============================================================
# CALCULO DE PROBABILIDADE
# ============================================================

def prob_over(valor, linha, escala=1.0):

    if linha <= 0:
        return 0.0

    probabilidade = (valor / linha) * 50
    probabilidade = probabilidade * escala

    return round(
        max(0.0, min(probabilidade, 95.0)),
        2
    )


# ============================================================
# ANALISE DA PARTIDA
# ============================================================

def analisar_partida(jogo):

    mercados = []

    estatisticas = jogo.get("statistics", {})

    # --------------------------------------------------------
    # GOLS
    # --------------------------------------------------------

    gols = (
        estatisticas.get("home_goals", 0)
        + estatisticas.get("away_goals", 0)
    )

    mercados.append({
        "mercado": "gols",
        "linha": "Mais 2.5",
        "probabilidade": prob_over(gols, 2.5)
    })

    # --------------------------------------------------------
    # ESCANTEIOS
    # --------------------------------------------------------

    corners = (
        estatisticas.get("home_corners", 0)
        + estatisticas.get("away_corners", 0)
    )

    mercados.append({
        "mercado": "corners",
        "linha": "Mais 9.5",
        "probabilidade": prob_over(corners, 9.5)
    })

    # --------------------------------------------------------
    # CHUTES
    # --------------------------------------------------------

    shots = (
        estatisticas.get("home_shots", 0)
        + estatisticas.get("away_shots", 0)
    )

    mercados.append({
        "mercado": "shots",
        "linha": "Mais 24.5",
        "probabilidade": prob_over(shots, 24.5)
    })

    # --------------------------------------------------------
    # CHUTES NO ALVO
    # --------------------------------------------------------

    shots_on_target = (
        estatisticas.get("home_shots_on_target", 0)
        + estatisticas.get("away_shots_on_target", 0)
    )

    mercados.append({
        "mercado": "shots_on_target",
        "linha": "Mais 8.5",
        "probabilidade": prob_over(
            shots_on_target,
            8.5
        )
    })

    # --------------------------------------------------------
    # DESARMES
    # --------------------------------------------------------

    tackles = (
        estatisticas.get("home_tackles", 0)
        + estatisticas.get("away_tackles", 0)
    )

    mercados.append({
        "mercado": "tackles",
        "linha": "Mais 30.5",
        "probabilidade": prob_over(
            tackles,
            30.5
        )
    })

    # --------------------------------------------------------
    # CARTOES
    # --------------------------------------------------------

    cards = (
        estatisticas.get("home_cards", 0)
        + estatisticas.get("away_cards", 0)
    )

    mercados.append({
        "mercado": "cards",
        "linha": "Mais 4.5",
        "probabilidade": prob_over(
            cards,
            4.5
        )
    })

    # --------------------------------------------------------
    # FALTAS
    # --------------------------------------------------------

    fouls = (
        estatisticas.get("home_fouls", 0)
        + estatisticas.get("away_fouls", 0)
    )

    mercados.append({
        "mercado": "faltas",
        "linha": "Mais 25.5",
        "probabilidade": prob_over(
            fouls,
            25.5
        )
    })

    return mercados


# ============================================================
# MONTAR TALAO
# ============================================================

def montar_talao(mercados):

    elegiveis = [
        mercado
        for mercado in mercados
        if mercado["probabilidade"] >= FILTRO_MINIMO
    ]

    elegiveis.sort(
        key=lambda x: x["probabilidade"],
        reverse=True
    )

    selecionados = elegiveis[:MAX_SELECOES]

    descartados = [
        mercado
        for mercado in mercados
        if mercado not in selecionados
    ]

    return selecionados, descartados


# ============================================================
# BACKTEST
# ============================================================

def executar_backtest(historico):

    total = 0
    acertos = 0
    erros = 0

    resultados = []

    for jogo in historico:

        mercados = analisar_partida(jogo)

        selecionados, _ = montar_talao(mercados)

        resultado_real = jogo.get("result", {})

        if not selecionados:
            continue

        for mercado in selecionados:

            nome = mercado["mercado"]

            acertou = resultado_real.get(nome)

            if acertou is None:
                continue

            total += 1

            if acertou:
                acertos += 1
                status = "ACERTO"
            else:
                erros += 1
                status = "ERRO"

            resultados.append({
                "mercado": nome,
                "probabilidade": mercado["probabilidade"],
                "resultado": status
            })

    taxa = 0.0

    if total > 0:
        taxa = (acertos / total) * 100

    return {
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "taxa": round(taxa, 2),
        "resultados": resultados
    }


# ============================================================
# CARREGAR HISTORICO
# ============================================================

def carregar_historico():

    caminho = "data/history.json"

    if not os.path.exists(caminho):
        return []

    try:

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

        if not isinstance(dados, list):
            return []

        return dados

    except Exception as erro:

        print(
            "Erro ao carregar histórico:",
            erro
        )

        return []


#
