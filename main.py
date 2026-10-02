import json
import os
from datetime import datetime


# ============================================================
# BET-AI V13
# Sistema experimental de análise estatística de futebol
# ============================================================

VERSAO = "13.0"

FILTRO_MINIMO = 60.0
MAX_SELECOES = 3

ARQUIVO_HISTORICO = "historico.json"


# ============================================================
# DADOS DE EXEMPLO
# ============================================================

JOGO = {
    "home": "Time Casa",
    "away": "Time Fora",

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
# CONFIGURAÇÃO DOS MERCADOS
# ============================================================

MERCADOS = [
    {
        "nome": "goals",
        "descricao": "Gols",
        "linha": 2.5,
        "chave_casa": "goals_home",
        "chave_fora": "goals_away",
    },
    {
        "nome": "corners",
        "descricao": "Escanteios",
        "linha": 9.5,
        "chave_casa": "corners_home",
        "chave_fora": "corners_away",
    },
    {
        "nome": "shots",
        "descricao": "Chutes",
        "linha": 24.5,
        "chave_casa": "shots_home",
        "chave_fora": "shots_away",
    },
    {
        "nome": "shots_on_target",
        "descricao": "Chutes no alvo",
        "linha": 8.5,
        "chave_casa": "shots_on_target_home",
        "chave_fora": "shots_on_target_away",
    },
    {
        "nome": "tackles",
        "descricao": "Desarmes",
        "linha": 30.5,
        "chave_casa": "tackles_home",
        "chave_fora": "tackles_away",
    },
    {
        "nome": "cards",
        "descricao": "Cartões",
        "linha": 4.5,
        "chave_casa": "cards_home",
        "chave_fora": "cards_away",
    },
    {
        "nome": "fouls",
        "descricao": "Faltas",
        "linha": 25.5,
        "chave_casa": "fouls_home",
        "chave_fora": "fouls_away",
    },
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limitar(valor, minimo=0.0, maximo=99.0):
    return max(minimo, min(valor, maximo))


def classificacao(probabilidade):
    if probabilidade >= 80:
        return "ALTA"
    elif probabilidade >= 70:
        return "MEDIA"
    elif probabilidade >= 60:
        return "MEDIA"
    else:
        return "BAIXA"


def emoji_classificacao(classe):
    if classe == "ALTA":
        return "🟢"
    elif classe == "MEDIA":
        return "🟡"
    return "🔴"


# ============================================================
# CÁLCULO DE PROBABILIDADE
# ============================================================

def calcular_probabilidades(media, linha):
    """
    Modelo estatístico experimental.

    Quanto maior a distância da média em relação à linha,
    maior ou menor será a estimativa.

    IMPORTANTE:
    Não representa uma probabilidade real garantida.
    """

    if media <= 0:
        return 0.0, 100.0

    diferenca = media - linha

    # Base de 50%
    ajuste = (diferenca / max(linha, 1)) * 100

    prob_mais = 50 + ajuste * 0.65

    prob_mais = limitar(prob_mais, 1, 99)
    prob_menos = 100 - prob_mais

    return round(prob_mais, 2), round(prob_menos, 2)


# ============================================================
# SCORE
# ============================================================

def calcular_score(probabilidade):
    """
    Score interno utilizado apenas para ordenar os mercados.
    """

    if probabilidade >= 85:
        return 100

    if probabilidade >= 80:
        return 95

    if probabilidade >= 75:
        return 90

    if probabilidade >= 70:
        return 82

    if probabilidade >= 65:
        return 75

    if probabilidade >= 60:
        return 68

    return 50


# ============================================================
# ANALISAR MERCADO
# ============================================================

def analisar_mercado(jogo, mercado):
    casa = jogo[mercado["chave_casa"]]
    fora = jogo[mercado["chave_fora"]]

    media = casa + fora
    linha = mercado["linha"]

    prob_mais, prob_menos = calcular_probabilidades(
        media,
        linha
    )

    resultados = []

    # MAIS
    resultados.append({
        "market": mercado["nome"],
        "descricao": mercado["descricao"],
        "side": "Mais",
        "line": linha,
        "probability": prob_mais,
        "opposite": prob_menos,
        "score": calcular_score(prob_mais),
        "classification": classificacao(prob_mais),
        "media": round(media, 2),
    })

    # MENOS
    resultados.append({
        "market": mercado["nome"],
        "descricao": mercado["descricao"],
        "side": "Menos",
        "line": linha,
        "probability": prob_menos,
        "opposite": prob_mais,
        "score": calcular_score(prob_menos),
        "classification": classificacao(prob_menos),
        "media": round(media, 2),
    })

    return resultados


# ============================================================
# ANALISAR TODOS OS MERCADOS
# ============================================================

def analisar_jogo(jogo):
    mercados = []

    for mercado in MERCADOS:
        resultados = analisar_mercado(
            jogo,
            mercado
        )

        mercados.extend(resultados)

    return mercados


# ============================================================
# FILTRAR MERCADOS
# ============================================================

def filtrar_mercados(mercados):
    aprovados = []
    descartados = []

    for item in mercados:
        if item["probability"] >= FILTRO_MINIMO:
            aprovados.append(item)
        else:
            descartados.append(item)

    return aprovados, descartados


# ============================================================
# SELECIONAR MELHORES MERCADOS
# ============================================================

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
    mercados_usados = set()

    for item in ordenados:

        if len(selecionados) >= MAX_SELECOES:
            break

        nome_mercado = item["market"]

        # Evita Mais e Menos do mesmo mercado
        if nome_mercado in mercados_usados:
            continue

        selecionados.append(item)
        mercados_usados.add(nome_mercado)

    return selecionados


# ============================================================
# PROBABILIDADE MÉDIA
# ============================================================

def calcular_media_probabilidade(mercados):
    if not mercados:
        return 0.0

    total = sum(
        item["probability"]
        for item in mercados
    )

    return round(
        total / len(mercados),
        2
    )


# ============================================================
# HISTÓRICO
# ============================================================

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return []

    try:
        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:
            return json.load(arquivo)

    except Exception:
        return []


def salvar_historico(registro):
    historico = carregar_historico()

    historico.append(registro)

    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# BACKTEST
# ============================================================

def avaliar_resultado(probabilidade, resultado_real):
    """
    Função simples para o futuro módulo de backtest.

    resultado_real:
    True  = mercado acertou
    False = mercado errou
    """

    return {
        "probabilidade_modelo": probabilidade,
        "resultado_real": resultado_real,
        "acertou": bool(resultado_real),
    }


def calcular_metricas_backtest(resultados):
    if not resultados:
        return {
            "total": 0,
            "acertos": 0,
            "erros": 0,
            "taxa_acerto": 0.0,
        }

    acertos = sum(
        1 for resultado in resultados
        if resultado["acertou"]
    )

    total = len(resultados)
    erros = total - acertos

    taxa = (acertos / total) * 100

    return {
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "taxa_acerto": round(taxa, 2),
    }


# ============================================================
# RELATÓRIO
# ============================================================

def imprimir_estatisticas(jogo):
    print()
    print("========== ESTATISTICAS ==========")

    for mercado in MERCADOS:

        casa = jogo[mercado["chave_casa"]]
        fora = jogo[mercado["chave_fora"]]

        print(
            f'{mercado["descricao"]}: '
            f'Casa {casa} | Fora {fora}'
        )


def imprimir_probabilidades(mercados):
    print()
    print("========== PROBABILIDADES ==========")

    for item in mercados:

        classe = item["classification"]
        emoji = emoji_classificacao(classe)

        print(
            f'{item["descricao"]} - '
            f'{item["side"]} {item["line"]}: '
            f'{item["probability"]:.2f}% '
            f'[{emoji} {classe}]'
        )


# ============================================================
# TALÃO
# ============================================================

def imprimir_talao(selecionados):
    print()
    print("=" * 12 + " TALAO BET-AI V13 " + "=" * 12)

    if not selecionados:
        print("Nenhum mercado atingiu o filtro mínimo.")
        return

    for numero, item in enumerate(
        selecionados,
        start=1
    ):
        emoji = emoji_classificacao(
            item["classification"]
        )

        print(
            f'{numero}. '
            f'{item["descricao"]} - '
            f'{item["side"]} {item["line"]} '
            f'({item["probability"]:.2f}%) '
            f'[{emoji} {item["classification"]}]'
        )

    media = calcular_media_probabilidade(
        selecionados
    )

    print("-" * 50)
    print(f"Probabilidade média: {media:.2f}%")
    print(f"Filtro utilizado: {FILTRO_MINIMO:.0f}%")
    print(f"Máximo de seleções: {MAX_SELECOES}")


# ============================================================
# DESCARTADOS
# ============================================================

def imprimir_descartados(descartados):
    print()
    print("========== MERCADOS DESCARTADOS ==========")

    if not descartados:
        print("Nenhum mercado descartado.")
        return

    for item in descartados:

        emoji = emoji_classificacao(
            item["classification"]
        )

        print(
            f'- {item["descricao"]} - '
            f'{item["side"]} {item["line"]} '
            f'({item["probability"]:.2f}%) '
            f'[{emoji} {item["classification"]}]'
        )


# ============================================================
# RELATÓRIO DE BACKTEST
# ============================================================

def imprimir_backtest():
    print()
    print("========== BACKTEST ==========")

    historico = carregar_historico()

    if not historico:
        print(
            "Ainda não existem resultados "
            "históricos suficientes."
        )
        print(
            "O módulo de backtest está preparado "
            "para receber dados reais."
        )
        return

    resultados = []

    for registro in historico:

        if "acertou" in registro:
            resultados.append(
                registro
            )

    metricas = calcular_metricas_backtest(
        resultados
    )

    print(
        f'Total avaliado: {metricas["total"]}'
    )

    print(
        f'Acertos: {metricas["acertos"]}'
    )

    print(
        f'Erros: {metricas["erros"]}'
    )

    print(
        f'Taxa de acerto: '
        f'{metricas["taxa_acerto"]:.2f}%'
    )


# ============================================================
# SALVAR ANÁLISE
# ============================================================

def registrar_analise(
    jogo,
    selecionados
):

    registro = {
        "data": datetime.now().isoformat(),
        "versao": VERSAO,
        "home": jogo["home"],
        "away": jogo["away"],
        "filtro": FILTRO_MINIMO,
        "max_selecoes": MAX_SELECOES,
        "selecionados": selecionados,
    }

    historico = carregar_historico()

    historico.append(registro)

    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 50)
    print(f"BET-AI V{VERSAO}")
    print("SISTEMA DE ANALISE ESTATISTICA")
    print("=" * 50)

    print()
    print(
        f'Jogo: {JOGO["home"]} '
        f'x {JOGO["away"]}'
    )

    imprimir_estatisticas(JOGO)

    # Analisa todos os mercados
    todos = analisar_jogo(JOGO)

    # Mostra probabilidades
    imprimir_probabilidades(todos)

    # Filtra
    aprovados, descartados = filtrar_mercados(
        todos
    )

    # Seleciona máximo de 3
    selecionados = selecionar_mercados(
        aprovados
    )

    # Mostra talão
    imprimir_talao(selecionados)

    # Mostra descartados
    imprimir_descartados(descartados)

    # Salva histórico
    registrar_analise(
        JOGO,
        selecionados
    )

    # Backtest
    imprimir_backtest()

    print()
    print("=" * 50)
    print(
        "OBSERVAÇÃO:"
    )
    print(
        "As probabilidades são estimativas "
        "experimentais do modelo."
    )
    print(
        "Não representam garantia de resultado."
    )
    print("=" * 50)

    print()
    print(
        f"BET-AI V{VERSAO} FINALIZADO"
    )
    print("=" * 50)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
