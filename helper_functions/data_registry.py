"""Module where we load the data necessary for the module to operate."""

import numpy as np
import pandas as pd
import streamlit as st

from .classes.match import Match
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


# @st.cache_data
def get_subteams() -> list[Subteam]:
    all_subteams = []
    for team in ALL_TEAMS:
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
                all_subteams.append(subteam)

    return all_subteams


ALL_SUBTEAMS = get_subteams()


def get_matches() -> list[Match]:
    fpath = FpathRegistry.all_matches
    if not fpath.exists():
        return []
    match_df = pd.read_csv(fpath)
    match_df["start"] = pd.to_datetime(match_df["start"])
    return [Match.from_dataframe_entry(m, ALL_SUBTEAMS) for _, m in match_df.iterrows()]


ALL_MATCHES = get_matches()
print(ALL_MATCHES)
