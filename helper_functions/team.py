from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import streamlit as st

from .constants import DATAPATH, SPORTS_LIST
from .plotting import create_sports_num_plot

if TYPE_CHECKING:
    from .sport_event import SportEvent


def _get_val_color(val: str, rgb_colors: tuple[int, ...]) -> str:
    if val == "":
        return "background-color: rgba(0, 0, 0, 0.0)"
    if val == "R":
        return "background-color: rgba(100, 100, 100, 0.3)"
    if str(val) in "ABCDEF":
        return f"background-color: rgba({rgb_colors[0]}, {rgb_colors[1]}, {rgb_colors[2]}, 0.3)"
    return "background-color: rgba(0, 0, 255, 0.5)"


@dataclass
class Team:
    """Class to represent a team of players attending the sports week."""

    team_index: int
    """The index of the team."""

    color: str = field(init=False)
    """The hex color of the team in plots."""

    sports_fulfill_nums: dict = field(
        default_factory=lambda: {sport: 0 for sport in SPORTS_LIST}
    )
    """Rough estimate for how well this team fulfills the requirements for each of the sports."""

    _players: list = field(default_factory=list)
    """The list of players in the team."""

    def __post_init__(self):
        colors = ["#FF0000", "#0000FF", "#008000", "#FFFF00", "#800080"]
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
        return {sport: self.sports_fulfill_nums[sport] for sport in SPORTS_LIST}

    @property
    def rgb_colors(self) -> tuple[int, ...]:
        return tuple(int(self.color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    def __str__(self):
        return f"{self.name} ({self.player_num} players): {self.sports_fulfill_nums}"

    def create_backup(self):
        self.player_df.to_csv(Team.backup_path(self.team_index), index=False)

    def add_player(self, player: pd.Series):
        self._players.append(player)
        for sport in SPORTS_LIST:
            if player[sport]:
                self.sports_fulfill_nums[sport] += 1

    def remove_player(self, player: pd.Series):
        self._players.remove(player)
        for sport in SPORTS_LIST:
            if player[sport]:
                self.sports_fulfill_nums[sport] -= 1

    def set_players(self, players: pd.DataFrame):
        self._players = players.to_dict(orient="records")
        self.sports_fulfill_nums = {
            sport: np.sum(self.player_df[sport]) for sport in SPORTS_LIST
        }

    def get_necessity_index(
        self, player: pd.Series, sports_events: list[SportEvent]
    ) -> int:
        """Calculate an index that represents how much the team needs the player.
        The index is calculated as the sum of the difference between the minimum number of players
        required for each sport and the number of players currently in the team for that sport.
        """
        index = 0
        for event in sports_events:
            sport = event.sanitized_name
            if player[sport]:
                index += min(event.min_player_val - self.sports_fulfill_nums[sport], 0)
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
        self,
        sport: SportEvent,
        num_subteams: int | None = None,
        num_players_per_subteam: int | None = None,
        seed: int = 42,
    ) -> dict[str, pd.DataFrame]:
        """Get a dictionary of subteams for a specific sport."""
        if num_subteams is None:
            num_subteams = sport.num_subteams
        if num_players_per_subteam is None:
            num_players_per_subteam = sport.num_players_per_subteam
        avail_players = self.get_all_players_for_sport(
            sport.sanitized_name, [f"avail_{day.lower()}" for day in sport.days]
        )
        req_player_num = num_subteams * num_players_per_subteam
        assert req_player_num <= len(
            avail_players
        ), f"Not enough players (only {len(avail_players)}) in the team to create the requested number of subteams (at least {req_player_num} expected)."
        assert num_subteams <= 8, "We only support up to 8 subteams."
        is_priority = avail_players["num_sports"] == 1
        prio_sample = avail_players[is_priority]
        nonprio_sample = avail_players[~is_priority]
        subteams = {}
        for i in range(num_subteams):
            # First, sample as many players from the prio sample.
            if len(prio_sample) < num_players_per_subteam:
                subteam = prio_sample
                prio_sample = prio_sample.drop(subteam.index)
            else:
                subteam = prio_sample.sample(
                    num_players_per_subteam, replace=False, random_state=seed + i
                )
                prio_sample = prio_sample.drop(subteam.index)
            # Then, fill up with non-priority players.
            num_remaining = num_players_per_subteam - len(subteam)

            fill_players = nonprio_sample.sample(
                num_remaining, replace=False, random_state=seed + i
            )
            nonprio_sample = nonprio_sample.drop(fill_players.index)
            subteams["ABCDEFGH"[i]] = pd.concat([subteam, fill_players])
        for player in self._players:
            team_key = {
                k
                for k, team in subteams.items()
                if player["nickname"] in team["nickname"].tolist()
            }
            key = "" if len(team_key) == 0 else team_key.pop()
            if player["nickname"] in nonprio_sample["nickname"].tolist():
                key = "R"
            player[f"subteam_{sport.sanitized_name}"] = key
        return subteams

    def write_streamlit_rep(self):
        st.write(f"## {self.name}")
        df = self.player_df[
            [
                col
                for col in self.player_df.columns
                if "subteam_" in col or col == "nickname"
            ]
        ]
        from .sport_event_registry import SPORTS_EVENTS

        col_dict = {
            f"subteam_{event.sanitized_name}": event.icon
            for event in SPORTS_EVENTS.values()
        }
        column_configs = {
            f"subteam_{event.sanitized_name}": st.column_config.Column(
                label=event.icon, help=event.name, disabled=True
            )
            for event in SPORTS_EVENTS.values()
        }
        df = df.set_index("nickname")
        st.dataframe(
            df.style.apply(
                lambda row: [_get_val_color(val, self.rgb_colors) for val in row],
                axis=1,
            ),
            column_config=column_configs,
        )
