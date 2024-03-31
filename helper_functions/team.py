from dataclasses import dataclass, field

import pandas as pd

from .constants import SPORTS_DF
from .plotting import create_sports_num_plot


@dataclass
class Team:
    """Class to represent a team of players attending the sports week."""

    team_index: int
    """The index of the team."""
    color: str = "red"
    """The color of the team in plots."""
    sports_fulfill_nums: dict = field(
        default_factory=lambda: {sport: 0 for sport in SPORTS_DF["name"]}
    )
    """Rough estimate for how well this team fulfills the requirements for each of the sports."""
    _players: list = field(default_factory=list)
    """The list of players in the team."""

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

    def get_players_for_sport(self, sport: str) -> pd.DataFrame:
        return self.player_df[self.player_df[sport]]
