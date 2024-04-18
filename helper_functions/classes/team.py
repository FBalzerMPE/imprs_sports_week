from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import DATAPATH, SPORTS_LIST, FpathRegistry
from .subteam import Subteam


def _get_val_color(val: str, rgb_colors: tuple[int, ...]) -> str:
    if val == "R":
        return "background-color: rgba(100, 100, 100, 0.3)"
    try:
        int(val)
        return f"background-color: rgba({rgb_colors[0]}, {rgb_colors[1]}, {rgb_colors[2]}, 0.3)"
    except ValueError:
        return ""


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
        self.color = colors[self.team_index % len(colors)]

    def __len__(self):
        return len(self._players)

    @classmethod
    def from_backup(cls, team_index: int) -> Team:
        fpath = cls.backup_path(team_index)
        if not fpath.exists():
            raise FileNotFoundError(f"No backup found for team {team_index}.")
        players = pd.read_csv(fpath)
        for subteam_col in [col for col in players.columns if "subteam" in col]:
            players[subteam_col] = (
                players[subteam_col]
                .apply(
                    lambda x: (
                        str(int(x)) if isinstance(x, float) and not np.isnan(x) else x
                    )
                )
                .astype("object")
            )
        team = cls(team_index=team_index)
        team.set_players(players)
        return team

    @staticmethod
    def backup_path(team_index: int) -> Path:
        team_letter = "ABC"[team_index]
        return Team.backup_path_from_letter(team_letter)

    @staticmethod
    def backup_path_from_letter(letter: str) -> Path:
        return DATAPATH.joinpath(f"teams/team_{letter}.csv")

    @property
    def player_num(self) -> int:
        return len(self._players)

    @property
    def name(self) -> str:
        return f"Team {self.team_letter}"

    @property
    def team_letter(self) -> str:
        return "ABC"[self.team_index]

    @property
    def player_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self._players)
        # Do not use fillna("") here as this will break things!
        df["Team"] = self.name
        return df

    @property
    def current_sports_stats(self) -> dict[str, int]:
        return {sport: self.sports_fulfill_nums[sport] for sport in SPORTS_LIST}

    @property
    def rgb_colors(self) -> tuple[int, ...]:
        return tuple(int(self.color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    @property
    def cloth_color(self) -> str:
        return {"A": "dark", "B": "white", "C": "colorful"}[self.team_letter]

    def __str__(self):
        return f"{self.name} ({self.player_num} players): {self.sports_fulfill_nums}"

    def contains_player(self, player_name: str):
        return player_name in self.player_df["nickname"].tolist()

    def get_new_stats_with_player(self, player: pd.Series) -> dict[str, int]:
        stats = self.sports_fulfill_nums.copy()
        for sport in SPORTS_LIST:
            if player[sport]:
                stats[sport] += 1
        return stats

    def transfer_player(self, player_name: str, other: Team):
        """Move a player from this team to another team."""
        player = self.player_df[self.player_df["nickname"] == player_name].iloc[0]
        self.remove_player(player)
        other.add_player(player)

    def get_rgb_with_alpha(self, alpha: float = 0.5) -> tuple[int | float, ...]:
        return *(val / 255 for val in self.rgb_colors), alpha

    def create_backup(self):
        self.player_df.to_csv(Team.backup_path(self.team_index), index=False)

    def add_player(self, player: pd.Series, register_as_reserve=False):
        self._players.append(player)
        for sport in SPORTS_LIST:
            if player[sport]:
                self.sports_fulfill_nums[sport] += 1
        if not register_as_reserve:
            return
        from ..data_registry import get_subteams

        current_subteams = get_subteams()
        for sport in SPORTS_LIST:
            if not player[sport]:
                continue
            subset = [
                subteam
                for subteam in current_subteams.values()
                if subteam.sport == sport
                and subteam.is_reserve
                and subteam.main_team_letter == self.team_letter
            ]
            for subteam in subset:
                subteam.players.append(player["nickname"])
        self.add_subteam_keys(list(current_subteams.values()))
        self.create_backup()

    def remove_player(self, player: pd.Series):
        player_index = [player["nickname"] for player in self._players].index(
            player["nickname"]
        )
        self._players.pop(player_index)
        for sport in SPORTS_LIST:
            if player[sport]:
                self.sports_fulfill_nums[sport] -= 1

    def set_players(self, players: pd.DataFrame):
        self._players = players.to_dict(orient="records")
        self.sports_fulfill_nums = {
            sport: np.sum(self.player_df[sport]) for sport in SPORTS_LIST
        }

    def plot_sports_num(self):
        from ..plotting import create_sports_num_plot

        label = f"{self.name} ({self.player_num} players)"
        create_sports_num_plot(
            self.player_df,
            color=self.get_rgb_with_alpha(0.3),
            label=label,
            annotate_numbers=False,
            height=0.2,
            y_offset=-self.team_index * 0.2 + 0.2,
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

    def write_streamlit_rep(self):
        st.write(f"## {self.name}")
        df = self.player_df[
            [
                col
                for col in self.player_df.columns
                if "subteam_" in col or col == "nickname"
            ]
        ]
        df.insert(0, "impath", df["nickname"].apply(FpathRegistry.get_animal_pic_path))

        df = df.fillna("").sort_values("nickname")
        df["nickname"] = df["nickname"].apply(
            lambda x: x[:14] + "..." if len(x) > 14 else x
        )

        from ..sport_event_registry import SPORTS_EVENTS

        column_configs = {
            f"subteam_{event.sanitized_name}": st.column_config.Column(
                label=event.icon, help=event.name, disabled=True
            )
            for event in SPORTS_EVENTS.values()
        }
        column_configs["impath"] = st.column_config.ImageColumn("Avatar")
        column_configs["nickname"] = st.column_config.TextColumn("Nickname")
        style = df.style.apply(
            lambda row: [_get_val_color(val, self.rgb_colors) for val in row],
            axis=1,
        )
        st.write(
            f"If you're a member of team {self.team_letter}, it'd be great if you could wear *{self.cloth_color} clothing* when participating in the team events."
        )
        st.dataframe(
            style,
            column_config=column_configs,
            hide_index=True,
        )

    def add_subteam_keys(self, subteams: list[Subteam]):
        player_df = self.player_df
        for sport in SPORTS_LIST:
            subteams_sport = [subteam for subteam in subteams if subteam.sport == sport]
            key_map = {
                player: subteam.sub_key
                for subteam in subteams_sport
                for player in subteam.players
            }
            player_df[f"subteam_{sport}"] = player_df["nickname"].apply(
                lambda name: key_map.get(name, "")
            )
        player_df["num_sports_attending"] = player_df[
            [f"subteam_{sport}" for sport in SPORTS_LIST]
        ].apply(lambda row: len([val for val in row if val not in ["", "R"]]), axis=1)
        player_df["attendance_ratio"] = (
            player_df["num_sports_attending"] / player_df["num_sports"]
        )
        self.set_players(player_df)
