from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Subteam:
    """A subteam of a given team."""

    sport: str
    """The sanitized sport name."""

    main_team_letter: str
    """The letter of the team this subteam belongs to."""

    sub_key: str
    """The key of this subteam. Should be an integer, or 'R' for reserve."""

    players: list[str]
    """The nicknames of the players belonging to this sub-team."""

    @property
    def as_series(self) -> pd.Series:
        series_dict = {
            "sport": self.sport,
            "team_key": self.main_team_letter,
            "sub_key": self.sub_key,
            "full_key": self.full_key,
            "players": self.players,
        }
        return pd.Series(series_dict)

    @property
    def full_key(self) -> str:
        return f"{self.main_team_letter}: {self.sub_key}"

    @property
    def key_or_single(self) -> str:
        """This subteam's full key or player name if the
        team only consists of one player."""
        return (
            self.full_key
            if len(self.players) > 1
            else f"{self.main_team_letter}: {self.players[0]}"
        )

    @property
    def is_reserve(self) -> bool:
        return self.sub_key == "R"

    def add_col_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds the info about the players of the subteam to the given
        dataframe."""
        colname = "subteam_" + self.sport
        if not colname in df.columns:
            df[colname] = ""
        df.loc[np.in1d(df["nickname"].tolist(), self.players), colname] = self.sub_key
        return df

    def switch_player_with_other(
        self, player_a: str, player_b: str, other: Subteam, verbose: bool = False
    ):
        """Move `player_a` from `self` to `other` and replace them with `player_b`."""
        assert player_a in self.players and player_a not in other.players
        assert player_b in other.players and player_b
        assert self.sport == other.sport
        self.players.remove(player_a)
        other.players.append(player_a)
        other.players.remove(player_b)
        self.players.append(player_b)
        if verbose:
            print(
                f"{self.sport}: Switched out {player_a} with {player_b} from {self.full_key} to {other.full_key}"
            )
