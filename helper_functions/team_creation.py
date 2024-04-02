import numpy as np
import pandas as pd

from .constants import DATAPATH
from .sport_event_registry import SPORTS_EVENTS
from .team import Team
from .team_registry import get_backup_teams


def create_teams(
    player_data: pd.DataFrame,
    num_teams: int = 3,
    seed=34,
    from_backup=False,
    create_backup=False,
) -> list[Team]:
    """Create teams based on the player data."""
    if from_backup:
        return get_backup_teams(num_teams)
    player_data = player_data.sample(frac=1, random_state=seed).reset_index(drop=True)
    teams = [Team(i) for i in range(1, num_teams + 1)]
    # I'm aware that this is not the most efficient way to do this, but it's the most readable
    # and luckily the speed requirements are not that high.
    for _, player in player_data.iterrows():
        best_team_to_join = np.argmax(
            [
                team.get_necessity_index(player, list(SPORTS_EVENTS.values()))
                for team in teams
            ]
        )
        teams[best_team_to_join].add_player(player)
    if not create_backup:
        return teams
    for team in teams:
        fpath = DATAPATH.joinpath(f"teams/team_{team.team_index}.csv")
        team.player_df.to_csv(fpath, index=False)
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
    from .sport_event_registry import SPORTS_EVENTS

    team_sizes = [team.player_num for team in teams]
    equality_num: float = 0.0  # perfectly equal
    if not any(x != team_sizes[-1] for x in team_sizes):
        return 100  # Not even same sizes
    for sport in SPORTS_EVENTS:
        sports_stats = [team.current_sports_stats[sport] for team in teams]
        equality_num += np.std(sports_stats, axis=0) / np.mean(sports_stats)
    return equality_num
