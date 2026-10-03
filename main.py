import math
from statistics import mean


# ============================================================
# BET-AI V20
# VERSÃO CONSOLIDADA
# ============================================================

VERSAO = "V20"

# ------------------------------------------------------------
# CONFIGURAÇÕES PRINCIPAIS
# ------------------------------------------------------------

FILTRO_MINIMO = 0.60
MAX_SELECOES = 3

# Quando True, mostra mercados abaixo do filtro.
MOSTRAR_DESCARTADOS = True

# Backtest só será calculado quando houver histórico real.
HISTORICO_REAL = []


# ============================================================
# UTILIDADES
# ============================================================

def limitar(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, valor))


def pct(valor):
    return round(valor * 100, 2)


def classificacao(probabilidade):
    if probabilidade >= 0.80:
        return "ALTA"
    elif probabilidade >= 0.60:
        return "MEDIA"
    else:
        return "BAIXA"


def validar_numero(nome, valor):
    if not isinstance(valor, (int, float)):
        raise ValueError(
            f"{nome} precisa ser numérico."
        )

    if not math.isfinite(valor):
        raise ValueError(
            f"{nome} contém valor inválido."
        )

    if valor < 0:
        raise ValueError(
            f"{nome} não pode ser negativo."
        )


# ============================================================
# VALIDAÇÃO DO JOGO
# ============================================================

CAMPOS_NUMERICOS = [
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


def validar_jogo(game):

    campos_obrigatorios = [
        "home",
        "away",
    ] + CAMPOS_NUMERICOS

    faltando = [
        campo
        for campo in campos_obrigatorios
        if campo not in game
    ]

    if faltando:
        raise ValueError(
            "Campos ausentes: "
            + ", ".join(faltando)
        )

    for campo in CAMPOS_NUMERICOS:
        validar_numero(
            campo,
            game[campo]
        )

    return True


# ============================================================
# CONFIGURAÇÃO DOS MERCADOS
# ============================================================

MERCADOS = {

    "goals": {
        "nome": "gols",
        "linha": 2.5,
    },

    "corners": {
        "nome": "escanteios",
        "linha": 9.5,
    },

    "shots": {
        "nome": "chutes",
        "linha": 24.5,
    },

    "shots_on_target": {
        "nome": "chutes_no_alvo",
        "linha": 8.5,
    },

    "tackles": {
        "nome": "desarmes",
        "linha": 30.5,
    },

    "cards": {
        "nome": "cartoes",
        "linha": 4.5,
    },

    "fouls": {
        "nome": "faltas",
        "linha": 25.5,
    },
}


# ============================================================
# MÉDIA DO MERCADO
# ============================================================

def obter_total(game, mercado):

    home = game[f"{mercado}_home"]
    away = game[f"{mercado}_away"]

    return home + away


# ============================================================
# DISTRIBUIÇÃO DE POISSON
# ============================================================

def poisson_pmf(k, lamb):

    if lamb <= 0:

        if k == 0:
            return 1.0

        return 0.0

    return (
        math.exp(-lamb)
        * (lamb ** k)
        / math.factorial(k)
    )


def poisson_cdf(k, lamb):

    if k < 0:
        return 0.0

    total = 0.0

    for i in range(k + 1):

        total += poisson_pmf(
            i,
            lamb
        )

    return limitar(total)


def probabilidade_mais(lamb, linha):

    # Todas as linhas utilizadas terminam em .5.
    limite = int(
        math.floor(linha)
    ) + 1

    prob = 1.0 - poisson_cdf(
        limite - 1,
        lamb
    )

    return limitar(prob)


def probabilidade_menos(lamb, linha):

    limite = int(
        math.floor(linha)
    )

    prob = poisson_cdf(
        limite,
        lamb
    )

    return limitar(prob)


# ============================================================
# MODELO DE PROBABILIDADE
# ============================================================

def calcular_probabilidades(total, linha):

    # Proteção contra valores impossíveis.
    lamb = max(
        0.01,
        float(total)
    )

    prob_mais = probabilidade_mais(
        lamb,
        linha
    )

    prob_menos = probabilidade_menos(
        lamb,
        linha
    )

    # Normalização para manter a soma em 100%.
    soma = (
        prob_mais
        + prob_menos
    )

    if soma <= 0:

        prob_mais = 0.50
        prob_menos = 0.50

    else:

        prob_mais /= soma
        prob_menos /= soma

    return (
        limitar(prob_mais),
        limitar(prob_menos)
    )


# ============================================================
# SCORE
# ============================================================

def calcular_score(probabilidade):

    # Score experimental.
    # Não representa probabilidade real calibrada.

    if probabilidade >= 0.80:
        bonus = 0.10

    elif probabilidade >= 0.70:
        bonus = 0.05

    else:
        bonus = 0.0

    score = (
        probabilidade * 0.90
        + bonus
    )

    return round(
        limitar(score),
        4
    )


# ============================================================
# CRIAÇÃO DOS MERCADOS
# ============================================================

def criar_item(
    mercado,
    nome,
    linha,
    lado,
    probabilidade
):

    return {
        "market": mercado,
        "name": nome,
        "line": linha,
        "side": lado,
        "probability": round(
            probabilidade,
            6
        ),
        "score": calcular_score(
            probabilidade
        ),
        "classification": classificacao(
            probabilidade
        ),
    }


def gerar_mercados(game):

    mercados = []

    for chave, configuracao in MERCADOS.items():

        total = obter_total(
            game,
            chave
        )

        linha = configuracao["linha"]
        nome = configuracao["nome"]

        prob_mais, prob_menos = (
            calcular_probabilidades(
                total,
                linha
            )
        )

        mercados.append(
            criar_item(
                chave,
                nome,
                linha,
                "Mais",
                prob_mais
            )
        )

        mercados.append(
            criar_item(
                chave,
                nome,
                linha,
                "Menos",
                prob_menos
            )
        )

    return mercados


# ============================================================
# SELEÇÃO
# ============================================================

def selecionar_mercados(mercados):

    elegiveis = [
        item
        for item in mercados
        if item["probability"]
        >= FILTRO_MINIMO
    ]

    elegiveis.sort(
        key=lambda item: (
            item["score"],
            item["probability"]
        ),
        reverse=True
    )

    selecionados = []

    mercados_usados = set()

    for item in elegiveis:

        mercado = item["market"]

        # Apenas um lado do mesmo mercado.
        if mercado in mercados_usados:
            continue

        selecionados.append(
            item
        )

        mercados_usados.add(
            mercado
        )

        if len(selecionados) >= MAX_SELECOES:
            break

    return selecionados


# ============================================================
# DESCARTADOS
# ============================================================

def obter_descartados(
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

    descartados = []

    for item in mercados:

        identificador = (
            item["market"],
            item["side"],
            item["line"]
        )

        if identificador not in selecionados_ids:

            descartados.append(
                item
            )

    descartados.sort(
        key=lambda item: item["probability"],
        reverse=True
    )

    return descartados


# ============================================================
# IMPRESSÃO DAS ESTATÍSTICAS
# ============================================================

def imprimir_estatisticas(game):

    print()
    print("=" * 55)
    print("ESTATISTICAS DA PARTIDA")
    print("=" * 55)

    print(
        f"Gols: Casa {game['goals_home']:.2f} "
        f"| Fora {game['goals_away']:.2f}"
    )

    print(
        f"Escanteios: Casa {game['corners_home']:.2f} "
        f"| Fora {game['corners_away']:.2f}"
    )

    print(
        f"Chutes: Casa {game['shots_home']:.2f} "
        f"| Fora {game['shots_away']:.2f}"
    )

    print(
        f"Chutes no alvo: Casa "
        f"{game['shots_on_target_home']:.2f} "
        f"| Fora "
        f"{game['shots_on_target_away']:.2f}"
    )

    print(
        f"Desarmes: Casa {game['tackles_home']:.2f} "
        f"| Fora {game['tackles_away']:.2f}"
    )

    print(
        f"Cartoes: Casa {game['cards_home']:.2f} "
        f"| Fora {game['cards_away']:.2f}"
    )

    print(
        f"Faltas: Casa {game['fouls_home']:.2f} "
        f"| Fora {game['fouls_away']:.2f}"
    )


# ============================================================
# IMPRESSÃO DAS PROBABILIDADES
# ============================================================

def imprimir_probabilidades(mercados):

    print()
    print("=" * 55)
    print("PROBABILIDADES")
    print("=" * 55)

    for item in mercados:

        print(
            f"- {item['name']} - "
            f"{item['side']} {item['line']:.1f} "
            f"("
            f"{pct(item['probability']):.2f}%"
            f") "
            f"[{item['classification']}]"
        )


# ============================================================
# TALÃO
# ============================================================

def imprimir_talao(selecionados):

    print()
    print("=" * 55)
    print(f"TALAO BET-AI {VERSAO}")
    print("=" * 55)

    if not selecionados:

        print(
            "Nenhum mercado atingiu "
            "o filtro mínimo."
        )

        print(
            f"Filtro: {pct(FILTRO_MINIMO):.0f}%"
        )

        return

    for numero, item in enumerate(
        selecionados,
        start=1
    ):

        print(
            f"{numero}. "
            f"{item['name']} - "
            f"{item['side']} {item['line']:.1f} "
            f"("
            f"{pct(item['probability']):.2f}%"
            f") "
            f"[{item['classification']}]"
        )

    media_probabilidade = mean(
        item["probability"]
        for item in selecionados
    )

    media_score = mean(
        item["score"]
        for item in selecionados
    )

    print("-" * 55)

    print(
        f"Probabilidade média: "
        f"{pct(media_probabilidade):.2f}%"
    )

    print(
        f"Score médio: "
        f"{pct(media_score):.2f}%"
    )

    print(
        f"Filtro utilizado: "
        f"{pct(FILTRO_MINIMO):.0f}%"
    )

    print(
        f"Máximo de seleções: "
        f"{MAX_SELECOES}"
    )


# ============================================================
# DESCARTADOS
# ============================================================

def imprimir_descartados(descartados):

    if not MOSTRAR_DESCARTADOS:
        return

    print()
    print("=" * 55)
    print("MERCADOS DESCARTADOS")
    print("=" * 55)

    if not descartados:

        print(
            "Nenhum mercado descartado."
        )

        return

    for item in descartados:

        print(
            f"- {item['name']} - "
            f"{item['side']} {item['line']:.1f} "
            f"("
            f"{pct(item['probability']):.2f}%"
            f") "
            f"[{item['classification']}]"
        )


# ============================================================
# RESULTADO REAL
# ============================================================

def verificar_resultado(
    item,
    resultado
):

    mercado = item["market"]
    lado = item["side"]
    linha = item["line"]

    if mercado not in resultado:
        return None

    valor_real = resultado[
        mercado
    ]

    if lado == "Mais":

        return valor_real > linha

    return valor_real < linha


# ============================================================
# BACKTEST
# ============================================================

def executar_backtest(historico):

    print()
    print("=" * 55)
    print("BACKTEST")
    print("=" * 55)

    if not historico:

        print(
            "Nenhum histórico real disponível."
        )

        print(
            "Backtest não calculado."
        )

        print(
            "Adicione resultados reais "
            "para medir o desempenho."
        )

        return {
            "avaliados": 0,
            "acertos": 0,
            "erros": 0,
            "taxa": None,
        }

    avaliados = 0
    acertos = 0
    erros = 0

    for jogo in historico:

        validar_jogo(jogo)

        if "resultado" not in jogo:
            continue

        mercados = gerar_mercados(
            jogo
        )

        selecionados = selecionar_mercados(
            mercados
        )

        for item in selecionados:

            acertou = verificar_resultado(
                item,
                jogo["resultado"]
            )

            if acertou is None:
                continue

            avaliados += 1

            if acertou:
                acertos += 1
            else:
                erros += 1

    if avaliados == 0:

        taxa = None

    else:

        taxa = (
            acertos / avaliados
        ) * 100

    print(
        f"Total avaliado: {avaliados}"
    )

    print(
        f"Acertos: {acertos}"
    )

    print(
        f"Erros: {erros}"
    )

    if taxa is None:

        print(
            "Taxa de acerto: N/A"
        )

    else:

        print(
            f"Taxa de acerto: "
            f"{taxa:.2f}%"
        )

    return {
        "avaliados": avaliados,
        "acertos": acertos,
        "erros": erros,
        "taxa": taxa,
    }


# ============================================================
# TESTES INTERNOS
# ============================================================

def executar_testes_internos():

    print()
    print("=" * 55)
    print("TESTES INTERNOS")
    print("=" * 55)

    # Teste 1
    assert (
        classificacao(0.85)
        == "ALTA"
    )

    # Teste 2
    assert (
        classificacao(0.65)
        == "MEDIA"
    )

    # Teste 3
    assert (
        classificacao(0.50)
        == "BAIXA"
    )

    # Teste 4
    mais, menos = (
        calcular_probabilidades(
            10.0,
            9.5
        )
    )

    assert (
        abs(
            (mais + menos) - 1.0
        ) < 0.000001
    )

    # Teste 5
    mercados = gerar_mercados(
        JOGO_TESTE
    )

    assert len(
        mercados
    ) == 14

    # Teste 6
    selecionados = selecionar_mercados(
        mercados
    )

    assert len(
        selecionados
    ) <= MAX_SELECOES

    # Teste 7
    nomes = [
        item["market"]
        for item in selecionados
    ]

    assert len(nomes) == len(
        set(nomes)
    )

    print(
        "✓ Classificação"
    )

    print(
        "✓ Probabilidades"
    )

    print(
        "✓ Soma das probabilidades"
    )

    print(
        "✓ Geração dos mercados"
    )

    print(
        "✓ Limite de seleções"
    )

    print(
        "✓ Bloqueio de mercados duplicados"
    )

    print()
    print(
        "TODOS OS TESTES INTERNOS PASSARAM."
    )


# ============================================================
# JOGO DE TESTE
# ============================================================

JOGO_TESTE = {

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
}


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 55)
    print(f"BET-AI {VERSAO}")
    print("VERSAO CONSOLIDADA")
    print("=" * 55)

    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    validar_jogo(
        JOGO_TESTE
    )

    # --------------------------------------------------------
    # TESTES INTERNOS
    # --------------------------------------------------------

    executar_testes_internos()

    # --------------------------------------------------------
    # ESTATÍSTICAS
    # --------------------------------------------------------

    imprimir_estatisticas(
        JOGO_TESTE
    )

    # --------------------------------------------------------
    # MERCADOS
    # --------------------------------------------------------

    mercados = gerar_mercados(
        JOGO_TESTE
    )

    imprimir_probabilidades(
        mercados
    )

    # --------------------------------------------------------
    # SELEÇÃO
    # --------------------------------------------------------

    selecionados = selecionar_mercados(
        mercados
    )

    imprimir_talao(
        selecionados
    )

    # --------------------------------------------------------
    # DESCARTADOS
    # --------------------------------------------------------

    descartados = obter_descartados(
        mercados,
        selecionados
    )

    imprimir_descartados(
        descartados
    )

    # --------------------------------------------------------
    # BACKTEST
    # --------------------------------------------------------

    executar_backtest(
        HISTORICO_REAL
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 55)
    print("OBSERVAÇÃO")
    print("=" * 55)

    print(
        "As probabilidades são estimativas "
        "experimentais do modelo."
    )

    print(
        "Elas não representam garantia "
        "de resultado."
    )

    print(
        "O backtest só deve usar "
        "resultados reais."
    )

    print()
    print("=" * 55)
    print(
        f"BET-AI {VERSAO} FINALIZADO"
    )
    print("=" * 55)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
