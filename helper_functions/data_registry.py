"""Module where we load the data necessary for the module to operate."""

import pandas as pd

from .classes.match import Match
from .classes.sport_location import SportLocation
from .classes.subteam import Subteam
from .classes.team import Team
from .constants import SPORTS_LIST, FpathRegistry


# @st.cache_data
def get_teams(num_teams: int = 3) -> list[Team]:
    """Get the teams from the backup files."""
    teams = []
    for i in range(num_teams):
        try:
            teams.append(Team.from_backup(i))
        except (FileNotFoundError, KeyError):
            pass
    return teams


ALL_TEAMS = get_teams()


def get_players(from_teams: bool = True) -> pd.DataFrame:
    """Loads a dataframe of all players."""
    if from_teams:
        return pd.concat([team.player_df for team in get_teams()])
    return pd.read_csv(FpathRegistry.all_responses)


# @st.cache_data
def get_subteams() -> dict[str, Subteam]:
    all_subteams = {}
    for team in get_teams():
        df = team.player_df
        for sport in SPORTS_LIST:
            column = df[f"subteam_{sport}"]
            for team_key in column[column.notna()].unique():
                players = df[column == team_key]["nickname"].tolist()
                subteam = Subteam(
                    sport,
                    main_team_letter=team.team_letter,
                    sub_key=team_key,
                    players=players,
                )
                all_subteams[sport + "_" + subteam.full_key] = subteam

    return all_subteams


ALL_SUBTEAMS = get_subteams()


def get_match_df() -> pd.DataFrame:
    fpath = FpathRegistry.all_matches
    if not fpath.exists():
        return pd.DataFrame()
    match_df = pd.read_csv(fpath)
    match_df["start"] = pd.to_datetime(match_df["start"])
    return match_df


def get_matches() -> list[Match]:
    match_df = get_match_df()
    subteams = get_subteams()
    try:
        return [Match.from_dataframe_entry(m, subteams) for _, m in match_df.iterrows()]
    except KeyError:
        return []


ALL_MATCHES = get_matches()
