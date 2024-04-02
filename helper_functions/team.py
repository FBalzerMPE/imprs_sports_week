from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from .constants import DATAPATH, SPORTS_DF
from .plotting import create_sports_num_plot

if TYPE_CHECKING:
    from .sport_event import SportEvent


@dataclass
class Team:
    """Class to represent a team of players attending the sports week."""

    team_index: int
    """The index of the team."""

    color: str = field(init=False)
    """The color of the team in plots."""

    sports_fulfill_nums: dict = field(
        default_factory=lambda: {sport: 0 for sport in SPORTS_DF["name"]}
    )
    """Rough estimate for how well this team fulfills the requirements for each of the sports."""

    _players: list = field(default_factory=list)
    """The list of players in the team."""

    def __post_init__(self):
        colors = ["red", "blue", "green", "yellow", "purple"]
        self.color = colors[self.team_index - 1 % len(colors)]

    @classmethod
    def from_backup(cls, team_index: int) -> Team:
        fpath = cls.backup_path(team_index)
        if not fpath.exists():
            raise FileNotFoundError(f"No backup found for team {team_index}.")
        players = pd.read_csv(fpath)
        team = cls(team_index=team_index)
        team.set_players(players)
        return team

    @staticmethod
    def backup_path(team_index) -> Path:
        return DATAPATH.joinpath(f"teams/team_{team_index}.csv")

    @property
    def player_num(self) -> int:
        return len(self._players)

    @property
    def name(self) -> str:
        return f"Team {self.team_index}"

    @property
    def player_df(self) -> pd.DataFrame:
        return pd.DataFrame(self._players)

    @property
    def current_sports_stats(self) -> dict[str, int]:
        return {sport: self.sports_fulfill_nums[sport] for sport in SPORTS_DF["name"]}

    def __str__(self):
        return f"{self.name} ({self.player_num} players): {self.sports_fulfill_nums}"

    def create_backup(self):
        self.player_df.to_csv(Team.backup_path(self.team_index), index=False)

    def add_player(self, player: pd.Series):
        self._players.append(player)
        for sport in SPORTS_DF["name"]:
            if player[sport]:
                self.sports_fulfill_nums[sport] += 1

    def remove_player(self, player: pd.Series):
        self._players.remove(player)
        for sport in SPORTS_DF["name"]:
            if player[sport]:
                self.sports_fulfill_nums[sport] -= 1

    def set_players(self, players: pd.DataFrame):
        self._players = players.to_dict(orient="records")
        self.sports_fulfill_nums = {
            sport: np.sum(self.player_df[sport]) for sport in SPORTS_DF["name"]
        }

    def get_necessity_index(self, player: pd.Series) -> int:
        """Calculate an index that represents how much the team needs the player.
        The index is calculated as the sum of the difference between the minimum number of players
        required for each sport and the number of players currently in the team for that sport.
        """
        index = 0
        for sport, val in SPORTS_DF[["name", "min_val"]].itertuples(index=False):
            if player[sport]:
                index += min(val - self.sports_fulfill_nums[sport], 0)
        index += 30 - self.player_num
        return index

    def plot_sports_num(self):
        label = f"{self.name} ({self.player_num} players)"
        create_sports_num_plot(
            self.player_df,
            color=self.color,
            label=label,
            alpha=0.3,
            annotate_numbers=False,
            height=0.2,
            y_offset=self.team_index * 0.2 - 0.2,
        )

    def get_all_players_for_sport(
        self, sport: str, sport_day_keys: list[str] | None = None
    ) -> pd.DataFrame:
        """Get all players in the team that are available for a specific sport, and optionally
        for specific days of the week, given in the 'avail_{day}' columns.

        Parameters
        ----------
        sport : str
            The name of the sport.
        sport_day_keys : list[str], optional
            The keys for the days of the week, by default None"""
        avail = self.player_df[self.player_df[sport]]
        if sport_day_keys is None:
            return avail
        return avail[avail[sport_day_keys].any(axis=1)]

    def get_subteams_for_sport(
        self, sport: SportEvent, num_subteams: int, size_subteams: int, seed: int = 42
    ) -> dict[str, pd.DataFrame]:
        """Get a dictionary of subteams for a specific sport."""
        assert (
            num_subteams * size_subteams <= self.sports_fulfill_nums[sport.df_key]
        ), "Not enough players in the team to create the requested number of subteams."
        assert num_subteams <= 8, "We only support up to 8 subteams."
        avail_players = self.get_all_players_for_sport(
            sport.df_key, [f"avail_{day.lower()}" for day in sport.days]
        )
        subteams = {}
        for i in range(num_subteams):
            subteam = avail_players.sample(
                size_subteams, replace=False, random_state=seed + i
            )
            avail_players = avail_players.drop(subteam.index)
            subteams["ABCDEFGH"[i]] = subteam
        return subteams
