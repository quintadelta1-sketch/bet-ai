import csv
import math
import os
from datetime import datetime


# ============================================================
# BET-AI FINAL 1.0
# Núcleo de análise estatística de futebol
# ============================================================

CONFIG = {
    "filtro_minimo": 60.0,
    "max_selecoes": 3,
    "stake_padrao": 10.0,
}


# ============================================================
# UTILIDADES
# ============================================================

def limitar(valor, minimo=0.0, maximo=100.0):
    return max(minimo, min(maximo, float(valor)))


def classificacao(probabilidade):
    if probabilidade >= 75:
        return "ALTA"
    elif probabilidade >= 65:
        return "MEDIA"
    return "BAIXA"


def probabilidade_over(media, linha):
    """
    Estimativa simples baseada em distribuição de Poisson.
    Não representa garantia de resultado.
    """
    if media <= 0:
        return 0.0

    limite = math.floor(linha)

    acumulada = 0.0

    for k in range(limite + 1):
        acumulada += (
            math.exp(-media)
            * (media ** k)
            / math.factorial(k)
        )

    return limitar((1 - acumulada) * 100)


def probabilidade_under(media, linha):
    """
    Estimativa de probabilidade para Under.
    """
    if media <= 0:
        return 100.0

    limite = math.floor(linha)

    acumulada = 0.0

    for k in range(limite + 1):
        acumulada += (
            math.exp(-media)
            * (media ** k)
            / math.factorial(k)
        )

    return limitar(acumulada * 100)


def media_casa_fora(casa, fora):
    return (float(casa) + float(fora)) / 2


# ============================================================
# ANÁLISE DOS MERCADOS
# ============================================================

def analisar_mercados(jogo):

    mercados = []

    estatisticas = [
        ("goals", "Gols", 2.5, "goals"),
        ("corners", "Escanteios", 9.5, "corners"),
        ("shots", "Chutes", 24.5, "shots"),
        ("shots_on_target", "Chutes no alvo", 8.5, "shots_on_target"),
        ("tackles", "Desarmes", 30.5, "tackles"),
        ("cards", "Cartões", 4.5, "cards"),
        ("fouls", "Faltas", 25.5, "fouls"),
    ]

    for chave, nome, linha, _ in estatisticas:

        casa = float(jogo.get(f"home_{chave}", 0))
        fora = float(jogo.get(f"away_{chave}", 0))

        media = media_casa_fora(casa, fora)

        over = probabilidade_over(media, linha)
        under = probabilidade_under(media, linha)

        mercados.append({
            "mercado": chave,
            "nome": nome,
            "tipo": "Mais",
            "linha": linha,
            "probabilidade": round(over, 2),
            "classe": classificacao(over),
        })

        mercados.append({
            "mercado": chave,
            "nome": nome,
            "tipo": "Menos",
            "linha": linha,
            "probabilidade": round(under, 2),
            "classe": classificacao(under),
        })

    return mercados


# ============================================================
# FILTRO
# ============================================================

def selecionar_melhores(mercados):

    validos = [
        m for m in mercados
        if m["probabilidade"] >= CONFIG["filtro_minimo"]
    ]

    validos.sort(
        key=lambda x: x["probabilidade"],
        reverse=True
    )

    return validos[:CONFIG["max_selecoes"]]


# ============================================================
# TALÃO
# ============================================================

def gerar_talao(selecoes):

    print()
    print("=" * 55)
    print("                 TALÃO BET-AI")
    print("=" * 55)

    if not selecoes:
        print("Nenhum mercado atingiu o filtro mínimo.")
        return

    soma = 0

    for i, mercado in enumerate(selecoes, 1):

        print(
            f"{i}. "
            f"{mercado['nome']} - "
            f"{mercado['tipo']} "
            f"{mercado['linha']} "
            f"({mercado['probabilidade']:.2f}%) "
            f"[{mercado['classe']}]"
        )

        soma += mercado["probabilidade"]

    media = soma / len(selecoes)

    print("-" * 55)
    print(f"Probabilidade média estimada: {media:.2f}%")
    print(f"Mercados selecionados: {len(selecoes)}")
    print(f"Filtro mínimo: {CONFIG['filtro_minimo']:.2f}%")
    print("=" * 55)


# ============================================================
# BACKTEST
# ============================================================

def executar_backtest(historico):

    print()
    print("=" * 55)
    print("                    BACKTEST")
    print("=" * 55)

    total = 0
    acertos = 0
    erros = 0

    for jogo in historico:

        resultado = jogo.get("resultado")

        if not resultado:
            continue

        mercados = analisar_mercados(jogo)
        selecoes = selecionar_melhores(mercados)

        for mercado in selecoes:

            total += 1

            acertou = verificar_resultado(
                jogo,
                mercado
            )

            if acertou:
                acertos += 1
            else:
                erros += 1

    if total == 0:

        print("Nenhum resultado real disponível.")
        print("Backtest não calculado.")

        return

    taxa = (acertos / total) * 100

    print(f"Total avaliado: {total}")
    print(f"Acertos: {acertos}")
    print(f"Erros: {erros}")
    print(f"Taxa de acerto: {taxa:.2f}%")

    print()
    print(
        "IMPORTANTE: uma taxa de acerto passada "
        "não garante resultados futuros."
    )


# ============================================================
# VERIFICAÇÃO DE RESULTADOS
# ============================================================

def verificar_resultado(jogo, mercado):

    chave = mercado["mercado"]

    valor = jogo.get(f"resultado_{chave}")

    if valor is None:
        return False

    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return False

    linha = float(mercado["linha"])

    if mercado["tipo"] == "Mais":
        return valor > linha

    return valor < linha


# ============================================================
# CARREGAR CSV
# ============================================================

def carregar_csv(caminho):

    if not os.path.exists(caminho):
        return []

    jogos = []

    with open(
        caminho,
        "r",
        encoding="utf-8",
        newline=""
    ) as arquivo:

        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            jogos.append(dict(linha))

    return jogos


# ============================================================
# JOGO DE TESTE
# ============================================================

def jogo_teste():

    return {
        "home": "Time Casa",
        "away": "Time Fora",

        "home_goals": 1.8,
        "away_goals": 1.4,

        "home_corners": 5.8,
        "away_corners": 4.9,

        "home_shots": 14.2,
        "away_shots": 12.8,

        "home_shots_on_target": 5.1,
        "away_shots_on_target": 4.0,

        "home_tackles": 15.2,
        "away_tackles": 16.1,

        "home_cards": 2.1,
        "away_cards": 2.3,

        "home_fouls": 12.8,
        "away_fouls": 13.6,
    }


# ============================================================
# ANÁLISE PRINCIPAL
# ============================================================

def analisar_jogo(jogo):

    print()
    print("=" * 55)
    print("                 BET-AI")
    print("=" * 55)

    print(
        f"Jogo: {jogo.get('home', 'Casa')} "
        f"x "
        f"{jogo.get('away', 'Fora')}"
    )

    print()
    print("ESTATÍSTICAS")
    print("-" * 55)

    campos = [
        ("goals", "Gols"),
        ("corners", "Escanteios"),
        ("shots", "Chutes"),
        ("shots_on_target", "Chutes no alvo"),
        ("tackles", "Desarmes"),
        ("cards", "Cartões"),
        ("fouls", "Faltas"),
    ]

    for chave, nome in campos:

        casa = jogo.get(f"home_{chave}", 0)
        fora = jogo.get(f"away_{chave}", 0)

        print(
            f"{nome}: "
            f"Casa {casa} | Fora {fora}"
        )

    mercados = analisar_mercados(jogo)

    print()
    print("PROBABILIDADES")
    print("-" * 55)

    for mercado in mercados:

        print(
            f"- {mercado['nome']} - "
            f"{mercado['tipo']} "
            f"{mercado['linha']} "
            f"({mercado['probabilidade']:.2f}%) "
            f"[{mercado['classe']}]"
        )

    selecoes = selecionar_melhores(mercados)

    gerar_talao(selecoes)

    print()
    print("=" * 55)
    print("MERCADOS DESCARTADOS")
    print("=" * 55)

    descartados = [
        m for m in mercados
        if m["probabilidade"] < CONFIG["filtro_minimo"]
    ]

    for mercado in descartados:

        print(
            f"- {mercado['nome']} - "
            f"{mercado['tipo']} "
            f"{mercado['linha']} "
            f"({mercado['probabilidade']:.2f}%) "
            f"[{mercado['classe']}]"
        )

    print()
    print("=" * 55)
    print("OBSERVAÇÃO")
    print("=" * 55)

    print(
        "As probabilidades são estimativas "
        "experimentais do modelo."
    )

    print(
        "Não representam garantia de resultado."
    )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 55)
    print("             BET-AI FINAL 1.0")
    print("=" * 55)

    print(
        "Início:",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

    # --------------------------------------------------------
    # 1. Tentar carregar histórico
    # --------------------------------------------------------

    historico = carregar_csv(
        "data/resultados.csv"
    )

    # --------------------------------------------------------
    # 2. Se não houver dados reais, usar teste
    # --------------------------------------------------------

    if historico:

        print()
        print(
            f"Histórico encontrado: "
            f"{len(historico)} registros."
        )

        jogo = historico[-1]

    else:

        print()
        print(
            "Nenhum histórico real disponível."
        )

        print(
            "Executando modo de demonstração."
        )

        jogo = jogo_teste()

    # --------------------------------------------------------
    # 3. Analisar jogo
    # --------------------------------------------------------

    analisar_jogo(jogo)

    # --------------------------------------------------------
    # 4. Backtest
    # --------------------------------------------------------

    executar_backtest(historico)

    print()
    print("=" * 55)
    print("             BET-AI FINAL 1.0")
    print("                 FINALIZADO")
    print("=" * 55)


if __name__ == "__main__":
    main()
