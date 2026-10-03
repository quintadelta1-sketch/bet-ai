import json
import os
from statistics import mean


# ============================================================
# BET-AI FINAL 1.0
# Motor de análise + seleção + backtest
# ============================================================

FILTRO_MINIMO = 60.0
MAX_SELECOES = 3


# ============================================================
# UTILIDADES
# ============================================================

def nivel(probabilidade):
    if probabilidade >= 75:
        return "ALTA"
    elif probabilidade >= 60:
        return "MEDIA"
    return "BAIXA"


def prob_over(valor, linha, escala=1.0):
    if linha <= 0:
        return 0.0

    p = (valor / linha) * 50

    p = p * escala

    return round(max(0.0, min(p, 95.0)), 2)


# ============================================================
# ANALISE DE UMA PARTIDA
# ============================================================

def analisar_partida(jogo):
    mercados = []

    estatisticas = jogo.get("statistics", {})

    # -------------------------
    # GOLS
    # -------------------------

    gols = (
        estatisticas.get("home_goals", 0)
        + estatisticas.get("away_goals", 0)
    )

    p_gols_over = prob_over(gols, 2.5)

    mercados.append({
        "mercado": "gols",
        "linha": "Mais 2.5",
        "probabilidade": p_gols_over
    })

    # -------------------------
    # ESCANTEIOS
    # -------------------------

    corners = (
        estatisticas.get("home_corners", 0)
        + estatisticas.get("away_corners", 0)
    )

    p_corners = prob_over(corners, 9.5)

    mercados.append({
        "mercado": "corners",
        "linha": "Mais 9.5",
        "probabilidade": p_corners
    })

    # -------------------------
    # CHUTES
    # -------------------------

    shots = (
        estatisticas.get("home_shots", 0)
        + estatisticas.get("away_shots", 0)
    )

    p_shots = prob_over(shots, 24.5)

    mercados.append({
        "mercado": "shots",
        "linha": "Mais 24.5",
        "probabilidade": p_shots
    })

    # -------------------------
    # CHUTES NO ALVO
    # -------------------------

    shots_target = (
        estatisticas.get("home_shots_on_target", 0)
        + estatisticas.get("away_shots_on_target", 0)
    )

    p_target = prob_over(shots_target, 8.5)

    mercados.append({
        "mercado": "shots_on_target",
        "linha": "Mais 8.5",
        "probabilidade": p_target
    })

    # -------------------------
    # DESARMES
    # -------------------------

    tackles = (
        estatisticas.get("home_tackles", 0)
        + estatisticas.get("away_tackles", 0)
    )

    p_tackles = prob_over(tackles, 30.5)

    mercados.append({
        "mercado": "tackles",
        "linha": "Mais 30.5",
        "probabilidade": p_tackles
    })

    # -------------------------
    # CARTÕES
    # -------------------------

    cards = (
        estatisticas.get("home_cards", 0)
        + estatisticas.get("away_cards", 0)
    )

    p_cards = prob_over(cards, 4.5)

    mercados.append({
        "mercado": "cards",
        "linha": "Mais 4.5",
        "probabilidade": p_cards
    })

    # -------------------------
    # FALTAS
    # -------------------------

    fouls = (
        estatisticas.get("home_fouls", 0)
        + estatisticas.get("away_fouls", 0)
    )

    p_fouls = prob_over(fouls, 25.5)

    mercados.append({
        "mercado": "faltas",
        "linha": "Mais 25.5",
        "probabilidade": p_fouls
    })

    return mercados


# ============================================================
# TALAO
# ============================================================

def montar_talao(mercados):
    elegiveis = [
        m for m in mercados
        if m["probabilidade"] >= FILTRO_MINIMO
    ]

    elegiveis.sort(
        key=lambda x: x["probabilidade"],
        reverse=True
    )

    selecionados = elegiveis[:MAX_SELECOES]

    descartados = [
        m for m in mercados
        if m not in selecionados
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
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            return []

        return dados

    except Exception as erro:
        print("Erro ao carregar histórico:", erro)
        return []


# ============================================================
# EXECUCAO PRINCIPAL
# ============================================================

def main():

    print()
    print("========================================")
    print("        BET-AI FINAL 1.0")
    print("========================================")
    print()

    historico = carregar_historico()

    print("Histórico encontrado:", len(historico))
    print("Filtro mínimo:", FILTRO_MINIMO, "%")
    print("Máximo de seleções:", MAX_SELECOES)
    print()

    # --------------------------------------------------------
    # ANALISE DA PARTIDA MAIS RECENTE
    # --------------------------------------------------------

    if historico:

        jogo = historico[-1]

        nome_casa = jogo.get("home", "Casa")
        nome_fora = jogo.get("away", "Fora")

        print("========================================")
        print("ANÁLISE")
        print("========================================")

        print(f"Partida: {nome_casa} x {nome_fora}")
        print()

        mercados = analisar_partida(jogo)

        selecionados, descartados = montar_talao(mercados)

        print("TALÃO BET-AI")
        print("----------------------------------------")

        if selecionados:

            for i, mercado in enumerate(selecionados, 1):

                p = mercado["probabilidade"]

                print(
                    f"{i}. {mercado['mercado']} - "
                    f"{mercado['linha']} "
                    f"({p:.2f}%) [{nivel(p)}]"
                )

            media = mean(
                m["probabilidade"]
                for m in selecionados
            )

            print()
            print(f"Probabilidade média: {media:.2f}%")

        else:
            print("Nenhum mercado atingiu o filtro mínimo.")

        print()
        print("MERCADOS DESCARTADOS")
        print("----------------------------------------")

        for mercado in descartados:

            p = mercado["probabilidade"]

            print(
                f"- {mercado['mercado']} - "
                f"{mercado['linha']} "
                f"({p:.2f}%) [{nivel(p)}]"
            )

    else:

        print("Nenhum histórico real disponível.")
        print("Adicione dados em data/history.json.")

    # --------------------------------------------------------
    # BACKTEST
    # --------------------------------------------------------

    print()
    print("========================================")
    print("BACKTEST")
    print("========================================")

    resultado = executar_backtest(historico)

    print("Total avaliado:", resultado["total"])
    print("Acertos:", resultado["acertos"])
    print("Erros:", resultado["erros"])
    print(f"Taxa de acerto: {resultado['taxa']:.2f}%")

    print()
    print("========================================")
    print("OBSERVAÇÃO")
    print("========================================")
    print("As probabilidades são estimativas")
    print("experimentais do modelo.")
    print("Não representam garantia de resultado.")
    print()
    print("BET-AI FINAL 1.0 FINALIZADO")
    print("========================================")


if __name__ == "__main__":
    main()
