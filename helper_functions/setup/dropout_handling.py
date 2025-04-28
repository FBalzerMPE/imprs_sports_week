"""Functions to handle dopouts and late signups."""

import numpy as np
import pandas as pd

from ..data_registry import DATA_NOW
from ..logger import LOGGER


def move_player_to_subteam(
    nickname: str, sport: str, new_subteam: str, replaced_player: str | None = None
):
    """Load the table of players and set the subteam to the desired one"""
    assert sport in DATA_NOW.sport_events
    df = DATA_NOW.players.set_index("nickname", drop=False).fillna("")
    old_subteam = df.loc[nickname, f"subteam_{sport}"]
    player_team = df.loc[nickname, "Team"]
    if old_subteam == new_subteam:
        LOGGER.warning(f"New subteam and old subteam '{old_subteam}' are the same.")
        return
    log_msg = f"Moving '{nickname}' ({player_team}) from '{old_subteam}' to '{new_subteam}' in {sport}."
    LOGGER.info(log_msg)
    if (new_subteam != "") and (
        new_subteam not in list(np.unique(df[f"subteam_{sport}"]) + ["R", "D"])
    ):
        msg = f"Registering an unknown new subteam {new_subteam} for {sport}"
        LOGGER.warning(msg)
    df.loc[nickname, f"subteam_{sport}"] = new_subteam
    for team_letter in "ABC":
        fpath = hf.Team.backup_path_from_letter(team_letter)
        df[df["Team"] == f"Team {team_letter}"].to_csv(fpath, index=False)
    with hf.DATAPATH.joinpath("teams/changelog.txt").open("a", encoding="utf-8") as f:
        f.write(log_msg + "\n")
