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
    if linha
