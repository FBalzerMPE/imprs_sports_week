from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..logger import LOGGER


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
            "is_reserve": self.is_reserve,
        }
        return pd.Series(series_dict)

    @property
    def real_names(self) -> list[str]:
        """The clear names for each player, if the mapping is available."""
        from ..setup.setup_util import get_real_player_name

        return [get_real_player_name(player, False) for player in self.players]

    @property
    def full_key(self) -> str:
        """Full key for external representation."""
        return f"{self.main_team_letter}: {self.sub_key}"

    @property
    def short_key(self) -> str:
        """Minimum length key for internal use."""
        return self.main_team_letter + self.sub_key

    @property
    def key_or_single(self) -> str:
        """This subteam's full key or player name if the
        team only consists of one player."""
        return (
            f"{self.main_team_letter}: {self.players[0]}"
            if self.sport in ["ping_pong", "tennis", "chess"]
            else self.full_key
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

    def move_player_to_other(self, player: str, other: Subteam):
        """Move `player_a` from `self` to `other`."""
        assert player in self.players and player not in other.players
        assert self.sport == other.sport
        self.players.remove(player)
        other.players.append(player)

    def switch_player_with_other(self, player_a: str, player_b: str, other: Subteam):
        """Move `player_a` from `self` to `other` and replace them with `player_b`."""
        self.move_player_to_other(player_a, other)
        other.move_player_to_other(player_b, self)
        LOGGER.info(
            f"{self.sport}: Switched out {player_a} with {player_b} from {self.short_key} to {other.short_key}"
        )
