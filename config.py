import os


# ============================================================
# BET-AI V4 - CONFIGURAÇÃO
# ============================================================

VERSION = "BET-AI V4.0"

API_URL = "https://v3.football.api-sports.io"

# Secret configurado no GitHub
API_KEY_ENV = "API_FOOTBALL_KEY"


# ------------------------------------------------------------
# CONTROLE DE REQUISIÇÕES
# ------------------------------------------------------------

# Plano atual informado pela API:
# aproximadamente 10 requisições por minuto.

REQUEST_INTERVAL = 8

# Tempo máximo de espera de uma requisição HTTP
REQUEST_TIMEOUT = 30

# Tentativas adicionais em caso de erro temporário
MAX_RETRIES = 2


# ------------------------------------------------------------
# ANÁLISE
# ------------------------------------------------------------

# Para evitar gastar muitas requisições,
# começamos analisando somente 1 jogo.
MAX_GAMES = 1

# Quantidade de jogos históricos utilizados
HISTORY_GAMES = 10


# ------------------------------------------------------------
# PROBABILIDADES
# ------------------------------------------------------------

MIN_PROBABILITY = 65.0

HIGH_PROBABILITY = 75.0


# ------------------------------------------------------------
# FUNÇÕES
# ------------------------------------------------------------

def get_api_key():
    key = os.getenv(API_KEY_ENV)

    if not key:
        raise RuntimeError(
            "API_FOOTBALL_KEY não configurada."
        )

    return key
