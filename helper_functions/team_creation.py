from itertools import cycle

import numpy as np
import pandas as pd

from .constants import SPORTS_DF
from .team import Team


def create_teams(player_data: pd.DataFrame, num_teams: int = 3, seed=39) -> list[Team]:
    """Create teams based on the player data."""
    player_data = player_data.sample(frac=1, random_state=seed).reset_index(drop=True)
    colors = cycle(["red", "blue", "green", "yellow", "purple"])
    teams = [Team(i, color=color) for i, color in zip(range(1, num_teams + 1), colors)]
    # I'm aware that this is not the most efficient way to do this, but it's the most readable
    # and luckily the speed requirements are not that high.
    for _, player in player_data.iterrows():
        best_team_to_join = np.argmax(
            [team.get_necessity_index(player) for team in teams]
        )
        teams[best_team_to_join].add_player(player)
    return teams


def find_optimal_team_seed(
    player_data: pd.DataFrame, num_teams: int = 3, num_tries: int = 100
) -> int:
    """Find the seed that gives the most balanced teams."""
    assert num_tries < 200, "This function is not optimized for a high number of tries."
    seeds = {
        seed: calculate_team_balance(create_teams(player_data, num_teams, seed=seed))
        for seed in range(num_tries)
    }
    return min(seeds, key=lambda x: seeds[x])


def calculate_team_balance(teams: list[Team]) -> float:
    """Calculate the balance of the teams based on the number of players in each team."""
    team_sizes = [team.player_num for team in teams]
    equality_num: float = 0.0  # perfectly equal
    if not any(x != team_sizes[-1] for x in team_sizes):
        return 100  # Not even same sizes
    for sport in SPORTS_DF["name"]:
        sports_stats = [team.current_sports_stats[sport] for team in teams]
        equality_num += np.std(sports_stats, axis=0) / np.mean(sports_stats)
    return equality_num
