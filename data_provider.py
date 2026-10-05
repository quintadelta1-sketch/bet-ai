from api_client import FootballAPI


api = FootballAPI()


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
            info.get("status", {}).get(
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

        # MUITO IMPORTANTE
        # será utilizado no histórico
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
# HISTÓRICO
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


def calculate_team_form(
    team_id,
    season,
    games_required=10
):

    fixtures = get_team_recent_fixtures(
        team_id,
        season
    )

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

        home_id = home.get("id")
        away_id = away.get("id")

        home_goals = goals.get("home")
        away_goals = goals.get("away")

        # Jogo sem resultado
        if home_goals is None:
            continue

        if away_goals is None:
            continue

        # Equipe jogando em casa
        if team_id == home_id:

            team_goals = home_goals
            opponent_goals = away_goals

        # Equipe jogando fora
        elif team_id == away_id:

            team_goals = away_goals
            opponent_goals = home_goals

        else:

            continue

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

            "form": 0.5
        }

    # --------------------------------------------------------
    # CÁLCULO
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

    return {

        "played": played,

        "wins": wins,

        "draws": draws,

        "losses": losses,

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
            )
    }
