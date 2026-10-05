from api_client import FootballAPI


api = FootballAPI()


# ============================================================
# CONFIGURAÇÃO DO PLANO GRATUITO
# ============================================================

# Conforme a mensagem retornada pela API-Football,
# o plano gratuito disponível neste projeto permite
# histórico entre 2022 e 2024.

FREE_MIN_SEASON = 2022
FREE_MAX_SEASON = 2024


# ============================================================
# JOGOS DO DIA
# ============================================================

def get_fixtures(date):

    return api.get(
        "fixtures",
        {
            "date": date
        }
    )


def normalize_fixture(fixture):

    info = fixture.get(
        "fixture",
        {}
    )

    teams = fixture.get(
        "teams",
        {}
    )

    goals = fixture.get(
        "goals",
        {}
    )

    league = fixture.get(
        "league",
        {}
    )

    home = teams.get(
        "home",
        {}
    )

    away = teams.get(
        "away",
        {}
    )

    return {

        "fixture_id":
            info.get("id"),

        "date":
            info.get("date"),

        "status":
            info.get(
                "status",
                {}
            ).get(
                "short"
            ),

        "home":
            home.get("name"),

        "away":
            away.get("name"),

        "home_id":
            home.get("id"),

        "away_id":
            away.get("id"),

        "home_goals":
            goals.get("home"),

        "away_goals":
            goals.get("away"),

        "league":
            league.get("name"),

        "league_id":
            league.get("id"),

        # Temporada do jogo analisado
        "season":
            league.get("season")
    }


def get_real_games(date):

    fixtures = get_fixtures(date)

    games = []

    for fixture in fixtures:

        game = normalize_fixture(
            fixture
        )

        if not game["home"]:
            continue

        if not game["away"]:
            continue

        if not game["home_id"]:
            continue

        if not game["away_id"]:
            continue

        if not game["season"]:
            continue

        games.append(game)

    return games


# ============================================================
# HISTÓRICO DA EQUIPE
# ============================================================

def get_team_recent_fixtures(
    team_id,
    season
):

    if not season:

        raise RuntimeError(
            f"Temporada não encontrada "
            f"para a equipe {team_id}."
        )

    return api.get(
        "fixtures",
        {
            "team": team_id,
            "season": season
        }
    )


# ============================================================
# ESCOLHER TEMPORADA COMPATÍVEL
# ============================================================

def get_compatible_season(
    requested_season
):

    try:

        requested = int(
            requested_season
        )

    except (
        TypeError,
        ValueError
    ):

        raise RuntimeError(
            "Temporada inválida."
        )

    # --------------------------------------------------------
    # Temporadas disponíveis diretamente
    # --------------------------------------------------------

    if (
        FREE_MIN_SEASON
        <= requested
        <= FREE_MAX_SEASON
    ):

        return requested

    # --------------------------------------------------------
    # Temporada futura / não disponível
    # --------------------------------------------------------

    if requested > FREE_MAX_SEASON:

        print()
        print(
            f"Temporada {requested} "
            "não está disponível no "
            "plano gratuito."
        )

        print(
            f"Usando temporada histórica "
            f"compatível: {FREE_MAX_SEASON}"
        )

        return FREE_MAX_SEASON

    # --------------------------------------------------------
    # Temporada anterior ao limite
    # --------------------------------------------------------

    if requested < FREE_MIN_SEASON:

        print()
        print(
            f"Temporada {requested} "
            "não está disponível."
        )

        print(
            f"Usando temporada mínima "
            f"compatível: {FREE_MIN_SEASON}"
        )

        return FREE_MIN_SEASON


# ============================================================
# HISTÓRICO COM FALLBACK
# ============================================================

def get_team_history(
    team_id,
    requested_season
):

    compatible_season = (
        get_compatible_season(
            requested_season
        )
    )

    print(
        f"Histórico consultado: "
        f"{compatible_season}"
    )

    try:

        fixtures = get_team_recent_fixtures(
            team_id,
            compatible_season
        )

        return (
            fixtures,
            compatible_season
        )

    except RuntimeError as error:

        error_text = str(error)

        # ----------------------------------------------------
        # Se a API disser que a temporada não está disponível,
        # tentamos temporadas anteriores.
        # ----------------------------------------------------

        if (
            "Free plans do not have access"
            not in error_text
        ):

            raise

        print()
        print(
            "Temporada bloqueada pelo "
            "plano gratuito."
        )

        for fallback_season in [
            2023,
            2022
        ]:

            print(
                f"Tentando histórico "
                f"{fallback_season}..."
            )

            try:

                fixtures = (
                    get_team_recent_fixtures(
                        team_id,
                        fallback_season
                    )
                )

                return (
                    fixtures,
                    fallback_season
                )

            except RuntimeError:

                continue

        raise RuntimeError(
            f"Não foi possível obter "
            f"histórico compatível para "
            f"a equipe {team_id}."
        )


# ============================================================
# CÁLCULO DA FORMA
# ============================================================

def calculate_team_form(
    team_id,
    season,
    games_required=10
):

    fixtures, historical_season = (
        get_team_history(
            team_id,
            season
        )
    )

    # --------------------------------------------------------
    # Ordenar jogos mais recentes primeiro
    # --------------------------------------------------------

    fixtures.sort(

        key=lambda item:
            item.get(
                "fixture",
                {}
            ).get(
                "date",
                ""
            ),

        reverse=True
    )

    played = 0

    wins = 0
    draws = 0
    losses = 0

    goals_for = 0
    goals_against = 0

    # --------------------------------------------------------
    # PROCESSAR JOGOS
    # --------------------------------------------------------

    for fixture in fixtures:

        if played >= games_required:
            break

        teams = fixture.get(
            "teams",
            {}
        )

        goals = fixture.get(
            "goals",
            {}
        )

        home = teams.get(
            "home",
            {}
        )

        away = teams.get(
            "away",
            {}
        )

        home_id = home.get(
            "id"
        )

        away_id = away.get(
            "id"
        )

        home_goals = goals.get(
            "home"
        )

        away_goals = goals.get(
            "away"
        )

        # Ignorar jogo sem resultado
        if home_goals is None:
            continue

        if away_goals is None:
            continue

        # ----------------------------------------------------
        # EQUIPE CASA
        # ----------------------------------------------------

        if team_id == home_id:

            team_goals = home_goals

            opponent_goals = away_goals

        # ----------------------------------------------------
        # EQUIPE FORA
        # ----------------------------------------------------

        elif team_id == away_id:

            team_goals = away_goals

            opponent_goals = home_goals

        else:

            continue

        # ----------------------------------------------------
        # CONTADORES
        # ----------------------------------------------------

        played += 1

        goals_for += team_goals

        goals_against += opponent_goals

        if team_goals > opponent_goals:

            wins += 1

        elif team_goals == opponent_goals:

            draws += 1

        else:

            losses += 1

    # --------------------------------------------------------
    # SEM HISTÓRICO
    # --------------------------------------------------------

    if played == 0:

        return {

            "played": 0,

            "wins": 0,

            "draws": 0,

            "losses": 0,

            "goals_for_avg": 0,

            "goals_against_avg": 0,

            "points_per_game": 0,

            "form": 0.5,

            "historical_season":
                historical_season
        }

    # --------------------------------------------------------
    # PONTOS
    # --------------------------------------------------------

    points = (
        wins * 3
        + draws
    )

    points_per_game = (
        points / played
    )

    form = (
        points
        / (played * 3)
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    return {

        "played":
            played,

        "wins":
            wins,

        "draws":
            draws,

        "losses":
            losses,

        "goals_for_avg":
            round(
                goals_for / played,
                2
            ),

        "goals_against_avg":
            round(
                goals_against / played,
                2
            ),

        "points_per_game":
            round(
                points_per_game,
                2
            ),

        "form":
            round(
                form,
                4
            ),

        "historical_season":
            historical_season
    }
