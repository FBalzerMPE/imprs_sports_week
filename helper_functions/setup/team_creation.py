import numpy as np
import warnings
import pandas as pd

from ..constants import DATAPATH, SPORTS_LIST, FpathRegistry
from ..util import deprecated
from ..classes.team import Team
from ..team_registry import get_backup_teams


def create_teams(
    num_teams: int = 3,
    seed: int | None = None,
    overwrite=False,
) -> list[Team]:
    """Create teams based on the player data.
    If a seed is given, the players are randomly shuffled before being appointed.
    If no seed is given, they are sorted by the number of sports they attend such that
    the 'easy' ones are assigned last, which seems to work out best.
    """
    if any([Team.backup_path(i).exists() for i in range(3)]) and not overwrite:
        return get_backup_teams(num_teams)
    player_data = pd.read_csv(FpathRegistry.all_responses)
    if seed is None:
        player_data = player_data.sort_values(
            "num_sports",
            ascending=False,
        )
    else:
        player_data = player_data.sample(frac=1, random_state=seed).reset_index(
            drop=True
        )
    teams = [Team(i) for i in range(num_teams)]
    # I'm aware that this is not the most efficient way to do this, but it's the most readable
    # and luckily the speed requirements are not that high.
    for _, player in player_data.iterrows():
        best_team_to_join = find_best_team_to_join(teams, player)
        teams[best_team_to_join].add_player(player)
    if seed is None:
        # If this player is moved, we are pretty golden
        teams[0].transfer_player("Red Eel", teams[2])
    for team in teams:
        fpath = DATAPATH.joinpath(f"teams/team_{team.team_index}.csv")
        df = team.player_df
        good_cols = [
            col
            for col in df.columns
            if not "wants_" in col and col not in ["num_sports_not_avail", "late_entry"]
        ]
        df[good_cols].to_csv(fpath, index=False)
    return teams


@deprecated("We have settled to not use random generation anymore")
def find_optimal_team_seed(num_teams: int = 3, num_tries: int = 100) -> int:
    """Find the seed that gives the most balanced teams."""
    assert (
        num_tries < 5000
    ), "This function is not optimized for a high number of tries."
    seeds = {
        seed: calculate_team_balance(create_teams(num_teams, seed=seed))
        for seed in range(num_tries)
    }
    return min(seeds, key=lambda x: seeds[x])


def find_best_team_to_join(teams: list[Team], player: pd.Series) -> np.intp:
    """Find the best team to add the given player to."""
    equality_nums = []
    for i in range(3):
        equality_num = 0
        team_stats = [
            (
                teams[i].get_new_stats_with_player(player)
                if i == j
                else teams[j].current_sports_stats
            )
            for j in range(3)
        ]
        for sport in SPORTS_LIST:
            sports_stats = [stat[sport] for stat in team_stats]
            with warnings.catch_warnings():
                # When I ignored the ZeroDivision here, the team creation worked out well.
                warnings.simplefilter("ignore", RuntimeWarning)
                equality_num += np.std(sports_stats, axis=0) / np.mean(sports_stats)
        equality_nums.append(equality_num)
    return np.argmin(equality_nums)


def calculate_team_balance(teams: list[Team]) -> float:
    """Calculate the balance of the teams based on the number of players in each team."""
    team_sizes = [team.player_num for team in teams]
    equality_num: float = 0.0  # perfectly equal
    if any(x != team_sizes[-1] for x in team_sizes):
        return 100  # Not even same sizes
    for sport in SPORTS_LIST:
        sports_stats = [team.current_sports_stats[sport] for team in teams]
        equality_num += np.std(sports_stats, axis=0) / np.mean(sports_stats)
    return equality_num
