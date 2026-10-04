import json
import os
from datetime import datetime


# ============================================================
# BET-AI FINAL 1.1
# Leitura de jogos através do games.json
# ============================================================

VERSAO = "BET-AI FINAL 1.1"

FILTRO_MINIMO = 60.0
MAX_SELECOES = 3


# ============================================================
# CARREGAR JOGOS
# ============================================================

def carregar_jogos():
    arquivo = "games.json"

    if not os.path.exists(arquivo):
        print("ERRO: games.json não encontrado.")
        return []

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            jogos = json.load(f)

        if not isinstance(jogos, list):
            print("ERRO: games.json precisa conter uma lista de jogos.")
            return []

        return jogos

    except json.JSONDecodeError as erro:
        print("ERRO: JSON inválido.")
        print(erro)
        return []

    except Exception as erro:
        print("ERRO ao carregar games.json:")
        print(erro)
        return []


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limitar(valor, minimo=0.0, maximo=100.0):
    return max(minimo, min(maximo, valor))


def probabilidade_over(media, linha):
    if media <= 0:
        return 0.0

    diferenca = media - linha

    prob = 50 + (diferenca / max(linha, 1)) * 100

    return limitar(prob)


def probabilidade_under(media, linha):
    if media <= 0:
        return 0.0

    diferenca = linha - media

    prob = 50 + (diferenca / max(linha, 1)) * 100

    return limitar(prob)


def classificacao(probabilidade):
    if probabilidade >= 75:
        return "ALTA"
    elif probabilidade >= 60:
        return "MEDIA"
    else:
        return "BAIXA"


# ============================================================
# ANALISAR MERCADOS
# ============================================================

def analisar_jogo(jogo):

    gols = jogo.get("goals_home", 0) + jogo.get("goals_away", 0)
    corners = jogo.get("corners_home", 0) + jogo.get("corners_away", 0)
    shots = jogo.get("shots_home", 0) + jogo.get("shots_away", 0)
    shots_on_target = (
        jogo.get("shots_on_target_home", 0)
        + jogo.get("shots_on_target_away", 0)
    )
    tackles = jogo.get("tackles_home", 0) + jogo.get("tackles_away", 0)
    cards = jogo.get("cards_home", 0) + jogo.get("cards_away", 0)
    fouls = jogo.get("fouls_home", 0) + jogo.get("fouls_away", 0)

    mercados = []

    def adicionar(nome, linha, prob_over, prob_under):

        mercados.append({
            "mercado": nome,
            "linha": linha,
            "tipo": "Mais",
            "probabilidade": round(prob_over, 2),
            "nivel": classificacao(prob_over)
        })

        mercados.append({
            "mercado": nome,
            "linha": linha,
            "tipo": "Menos",
            "probabilidade": round(prob_under, 2),
            "nivel": classificacao(prob_under)
        })

    adicionar(
        "gols",
        2.5,
        probabilidade_over(gols, 2.5),
        probabilidade_under(gols, 2.5)
    )

    adicionar(
        "escanteios",
        9.5,
        probabilidade_over(corners, 9.5),
        probabilidade_under(corners, 9.5)
    )

    adicionar(
        "chutes",
        24.5,
        probabilidade_over(shots, 24.5),
        probabilidade_under(shots, 24.5)
    )

    adicionar(
        "chutes_no_alvo",
        8.5,
        probabilidade_over(shots_on_target, 8.5),
        probabilidade_under(shots_on_target, 8.5)
    )

    adicionar(
        "desarmes",
        30.5,
        probabilidade_over(tackles, 30.5),
        probabilidade_under(tackles, 30.5)
    )

    adicionar(
        "cartoes",
        4.5,
        probabilidade_over(cards, 4.5),
        probabilidade_under(cards, 4.5)
    )

    adicionar(
        "faltas",
        25.5,
        probabilidade_over(fouls, 25.5),
        probabilidade_under(fouls, 25.5)
    )

    return mercados


# ============================================================
# GERAR TALÃO
# ============================================================

def gerar_talao(mercados):

    candidatos = [
        mercado
        for mercado in mercados
        if mercado["probabilidade"] >= FILTRO_MINIMO
    ]

    candidatos.sort(
        key=lambda x: x["probabilidade"],
        reverse=True
    )

    return candidatos[:MAX_SELECOES]


# ============================================================
# EXIBIR JOGO
# ============================================================

def exibir_jogo(jogo):

    casa = jogo.get("home", "Casa")
    fora = jogo.get("away", "Fora")

    print()
    print("=" * 50)
    print("                    BET-AI")
    print("=" * 50)

    print(f"Jogo: {casa} x {fora}")

    print()
    print("ESTATÍSTICAS")
    print("-" * 50)

    print(
        f"Gols: Casa {jogo.get('goals_home', 0)} | "
        f"Fora {jogo.get('goals_away', 0)}"
    )

    print(
        f"Escanteios: Casa {jogo.get('corners_home', 0)} | "
        f"Fora {jogo.get('corners_away', 0)}"
    )

    print(
        f"Chutes: Casa {jogo.get('shots_home', 0)} | "
        f"Fora {jogo.get('shots_away', 0)}"
    )

    print(
        f"Chutes no alvo: Casa {jogo.get('shots_on_target_home', 0)} | "
        f"Fora {jogo.get('shots_on_target_away', 0)}"
    )

    print(
        f"Desarmes: Casa {jogo.get('tackles_home', 0)} | "
        f"Fora {jogo.get('tackles_away', 0)}"
    )

    print(
        f"Cartões: Casa {jogo.get('cards_home', 0)} | "
        f"Fora {jogo.get('cards_away', 0)}"
    )

    print(
        f"Faltas: Casa {jogo.get('fouls_home', 0)} | "
        f"Fora {jogo.get('fouls_away', 0)}"
    )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    inicio = datetime.now()

    print("=" * 50)
    print(VERSAO)
    print("=" * 50)
    print(f"Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}")

    jogos = carregar_jogos()

    if not jogos:
        print()
        print("Nenhum jogo disponível.")
        print("Verifique o arquivo games.json.")
        return

    print()
    print(f"Jogos carregados: {len(jogos)}")
    print("Fonte: games.json")

    total_jogos = 0

    for jogo in jogos:

        total_jogos += 1

        exibir_jogo(jogo)

        mercados = analisar_jogo(jogo)

        print()
        print("PROBABILIDADES")
        print("-" * 50)

        for mercado in mercados:

            print(
                f"- {mercado['mercado']} - "
                f"{mercado['tipo']} {mercado['linha']} "
                f"({mercado['probabilidade']:.2f}%) "
                f"[{mercado['nivel']}]"
            )

        talao = gerar_talao(mercados)

        print()
        print("=" * 50)
        print("              TALÃO BET-AI")
        print("=" * 50)

        if not talao:

            print("Nenhum mercado atingiu o filtro mínimo.")

        else:

            for numero, selecao in enumerate(talao, 1):

                print(
                    f"{numero}. "
                    f"{selecao['mercado']} - "
                    f"{selecao['tipo']} "
                    f"{selecao['linha']} "
                    f"({selecao['probabilidade']:.2f}%) "
                    f"[{selecao['nivel']}]"
                )

            media = sum(
                item["probabilidade"]
                for item in talao
            ) / len(talao)

            print()
            print(
                f"Probabilidade média: {media:.2f}%"
            )

        print()
        print("Filtro utilizado:", FILTRO_MINIMO, "%")
        print("Máximo de seleções:", MAX_SELECOES)

    print()
    print("=" * 50)
    print("RESUMO")
    print("=" * 50)

    print(f"Total de jogos analisados: {total_jogos}")

    print()
    print("OBSERVAÇÃO")
    print("-" * 50)
    print(
        "As probabilidades são estimativas experimentais "
        "do modelo."
    )
    print(
        "Não representam garantia de resultado."
    )

    print()
    print("=" * 50)
    print("BET-AI FINAL 1.1 FINALIZADO")
    print("=" * 50)


if __name__ == "__main__":
    main()
