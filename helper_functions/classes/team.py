from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import CURRENT_YEAR, SPORTS_LIST, FpathRegistry
from ..logger import LOGGER
from ..util import write_changelog_entry

if TYPE_CHECKING:
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

    _players: list[pd.Series] = field(default_factory=list)
    """The list of players in the team."""

    colors = ["#FF0000", "#0000FF", "#008000", "#FFFF00", "#800080"]

    def __post_init__(self):
        self.color = Team.colors[self.team_index % len(Team.colors)]

    def __len__(self):
        return len(self._players)

    @classmethod
    def from_backup(cls, team_index: int, year=CURRENT_YEAR) -> Team:
        fpath = cls.backup_path(team_index, year)
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
        for col in ["dropout_sports"]:
            if col in players.columns:
                players[col] = players[col].apply(eval)

        team = cls(
            team_index=team_index,
            sports_fulfill_nums={
                sport: 0 for sport in SPORTS_LIST if sport in players.columns
            },
        )
        team.set_players(players)
        return team

    @staticmethod
    def backup_path(team_index: int, year=CURRENT_YEAR) -> Path:
        team_letter = "ABCDEF"[team_index]
        return FpathRegistry.get_path_team(team_letter, year)

    @property
    def player_num(self) -> int:
        return len(self._players)

    @property
    def name(self) -> str:
        return f"Team {self.team_letter}"

    @property
    def team_letter(self) -> str:
        return "ABCDEF"[self.team_index]

    @property
    def player_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self._players)
        # Do not use fillna("") here as this will break things!
        df["Team"] = self.name
        return df

    @property
    def current_sports_stats(self) -> dict[str, int]:
        return {sport: self.sports_fulfill_nums.get(sport, 0) for sport in SPORTS_LIST}

    @property
    def rgb_colors(self) -> tuple[int, ...]:
        return tuple(int(self.color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    @property
    def cloth_color(self) -> str:
        return {"A": "dark", "B": "white", "C": "colorful"}[self.team_letter]

    def __str__(self):
        return f"{self.name} ({self.player_num} players): {self.sports_fulfill_nums}"

    def change_player_attribute(
        self, player_name: str, attr: str, value: Any, not_exist_okay=False
    ):
        """Change the attribute of a player in the team."""
        if not self.contains_player(player_name):
            if not_exist_okay:
                return
            LOGGER.warning(
                f"Player {player_name} not in team {self.team_letter}. Cannot change attribute."
            )
            return
        idx = np.where([p["nickname"] == player_name for p in self._players])[0][0]
        player = self._players[idx]
        if attr not in player:
            raise KeyError(f"Attribute {attr} not found in player {player_name}.")
        player[attr] = value
        self._players[idx] = player

    def get_player_attribute(self, player_name: str, attr: str) -> Any:
        """Get the attribute of a player in the team."""
        if not self.contains_player(player_name):
            LOGGER.warning(
                f"Player {player_name} not in team {self.team_letter}. Cannot get attribute."
            )
            return None
        idx = np.where([p["nickname"] == player_name for p in self._players])[0][0]
        player = self._players[idx]
        if attr not in player:
            raise KeyError(f"Attribute {attr} not found in player {player_name}.")
        return player[attr]

    def contains_player(self, player_name: str):
        return player_name in self.player_df["nickname"].tolist()

    def get_new_stats_with_player(self, player: pd.Series) -> dict[str, int]:
        stats = self.sports_fulfill_nums.copy()
        for sport in SPORTS_LIST:
            if player[sport]:
                stats[sport] += 1
        return stats

    def transfer_player_to_other_team(
        self, player_name: str, other: Team, register_as_reserve: bool = False
    ):
        """Move a player from this team to another team."""
        player = self.player_df[self.player_df["nickname"] == player_name].iloc[0]
        self.remove_player(player)
        other.add_player(player, register_as_reserve)
        msg = f"Moved {player_name} from team {self.team_letter} to team {other.team_letter}."
        LOGGER.info(msg)
        write_changelog_entry(msg, add_checkbox=True)
        self.create_backup(overwrite=True)
        other.create_backup(overwrite=True)

    def get_rgb_with_alpha(self, alpha: float = 0.5) -> tuple[int | float, ...]:
        return *(val / 255 for val in self.rgb_colors), alpha

    def create_backup(self, overwrite: bool = False):
        """Create a backup of the current team in the backup folder."""
        fpath = Team.backup_path(self.team_index)
        if fpath.exists() and not overwrite:
            raise FileExistsError(f"Backup file {fpath} already exists.")
        self.player_df.to_csv(fpath, index=False)

    def change_player_subteam(
        self,
        player_name: str,
        sport: str,
        player_to_replace_name: str,
        replacement_key: Literal["D", "R"] | str | None = "D",
        check_reserve: bool = True,
        log: bool = True,
    ):
        """Change the subteam of a player in the team.
        Writes a changelog entry for this change, for which you should check the box after you
        have notified the affected player about the change."""
        if player_name != "" and not self.contains_player(player_name):
            LOGGER.warning(
                f"Player {player_name} not in team {self.team_letter}. Cannot change subteam."
            )
            return
        sport_key = f"subteam_{sport}"
        if not self.contains_player(player_to_replace_name):
            msg = f"Player {player_to_replace_name} not in {self.name}. Cannot change subteam."
            LOGGER.warning(msg)
            raise ValueError(msg)
        subteam_key = self.get_player_attribute(player_to_replace_name, sport_key)
        if subteam_key == replacement_key:
            LOGGER.warning(
                f"Player {player_to_replace_name} already in {replacement_key} (where you're trying to replace to). Skipping the change."
            )
            return
        if (
            player_name != ""
            and check_reserve
            and self.get_player_attribute(player_name, sport_key) != "R"
        ):
            LOGGER.warning(
                f"Player {player_name} is not a reserve player. Skipping subteam change."
            )
            return
        if replacement_key is None:  # In that case, just switch subteams
            replacement_key = self.get_player_attribute(player_name, sport_key)
        msg = f"Subteam change in {self.name} for {sport}: {player_name} (-> {subteam_key}) <--> {player_to_replace_name} (-> {replacement_key})"
        if player_name == "":
            old_key = self.get_player_attribute(player_to_replace_name, sport_key)
            msg = f"Subteam change in {self.name} for {sport}: {player_to_replace_name} ({old_key}-> {replacement_key}) "
            if old_key != "R":
                msg += "WITHOUT REPLACEMENT"
            else:
                msg += "[removal from reserve]"
        else:
            self.change_player_attribute(player_name, sport_key, subteam_key)
        self.change_player_attribute(player_to_replace_name, sport_key, replacement_key)
        LOGGER.info(msg)
        if log:
            write_changelog_entry(msg, CURRENT_YEAR, add_checkbox=True)
        self.create_backup(overwrite=True)

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
        self.create_backup(overwrite=True)

    def remove_player(self, player: pd.Series):
        player = player.fillna("")
        nickname = player["nickname"]
        player_index = [p["nickname"] for p in self._players].index(nickname)
        self._players.pop(player_index)
        for sport in SPORTS_LIST:
            if player[sport]:
                self.sports_fulfill_nums[sport] -= 1
            sub_key = f"subteam_{sport}"
            if sub_key in player and (sub_key := player[sub_key]) != "":
                msg = f"When removing {nickname} from {self.name}, they are removed from subteam {self.team_letter}{sub_key} for {sport}."
                LOGGER.info(msg)
                write_changelog_entry(msg, add_checkbox=True)
                player[sub_key] = "R"

    def set_players(self, players: pd.DataFrame):
        self._players = players.to_dict(orient="records")  # type: ignore
        self.sports_fulfill_nums = {
            sport: np.sum(self.player_df[sport])
            for sport in SPORTS_LIST
            if sport in players.columns
        }

    def plot_sports_num(self):
        from ..streamlit_display.plotting import create_sports_num_plot

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

        from ..data_registry import DATA_NOW

        column_configs = {
            f"subteam_{event.sanitized_name}": st.column_config.Column(
                label=event.icon, help=event.name, disabled=True
            )
            for event in DATA_NOW.sport_events.values()
        }
        column_configs["impath"] = st.column_config.ImageColumn("Avatar")
        column_configs["nickname"] = st.column_config.TextColumn("Nickname")
        style = df.style.apply(
            lambda row: [_get_val_color(val, self.rgb_colors) for val in row],
            axis=1,
        )
        # st.write(
        #     f"If you're a member of team {self.team_letter}, it'd be great <span style='background-color:darkred; color:white;'>**if you could wear *{self.cloth_color} clothing***</span> when participating in the big team events.",
        #     unsafe_allow_html=True,
        # )
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
