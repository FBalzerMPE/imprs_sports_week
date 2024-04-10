from typing import TypeVar

import numpy as np
import pandas as pd

from ..classes.match import Match
from ..classes.subteam import Subteam
from ..constants import FpathRegistry
from ..util import deprecated, turn_series_list_to_dataframe

T = TypeVar("T")


def generate_round_robin_list(
    subteams: list[Subteam], max_match_number=2
) -> list[tuple[Subteam, Subteam]]:
    """Generate a round-robin list of matchups between the teams."""
    matches = []
    for team_1 in subteams:
        for team_2 in subteams:
            if team_1.main_team_letter == team_2.main_team_letter:
                continue
            match = (team_1, team_2)
            num_t1 = np.sum([team_1 in match for match in matches])
            num_t2 = np.sum([team_2 in match for match in matches])
            if (num_t1 < max_match_number) and (num_t2 < max_match_number):
                matches.append(match)
    return matches


@deprecated("We've settled on the other method to determine the matchups.")
def determine_matchups_for_sport(
    all_subteams: list[Subteam], sport: str, max_match_number=2
) -> list[tuple[Subteam, Subteam]]:
    """Determine matchups between the teams.

    Do this in a round-robin fashion, where each team plays
    against each other team in the same subteam-pool.
    """
    all_subteams = [
        subteam
        for subteam in all_subteams
        if subteam.sport == sport and not subteam.is_reserve
    ]
    num_teams = len(all_subteams)
    assert (
        num_teams % 3 == 0
    ), f"Please provide equal amount of subteams for each team, found {num_teams}"
    num_groups = int(num_teams / 3)
    matchups = []
    for subteam_key in range(num_groups):
        subteams = [
            team for team in all_subteams if int(team.sub_key) == subteam_key + 1
        ]
        matchups += generate_round_robin_list(subteams, max_match_number)
    return matchups


def create_combinations(
    list1: list[T], list2: list[T], list3: list[T]
) -> list[tuple[T, T]]:
    """Create rotated combinations of the given lists.

    Example:

        list1 = ['A1', 'A2', 'A3']
        list2 = ['B1', 'B2', 'B3']
        list3 = ['C1', 'C2', 'C3']

        >>> create_combinations(list1, list2, list3)
            [('A1', 'B2'),
            ('B2', 'C3'),
            ('C3', 'A1'),
            ('A2', 'B3'),
            ('B3', 'C1'),
            ('C1', 'A2'),
            ('A3', 'B1'),
            ('B1', 'C2'),
            ('C2', 'A3')]
    """
    n = len(list1)
    combinations = []
    for i in range(n):
        combinations.append((list1[i], list2[(i + 1) % n]))
        combinations.append((list2[(i + 1) % n], list3[(i + 2) % n]))
        combinations.append((list3[(i + 2) % n], list1[(i + 3) % n]))
    return combinations


def determine_rotated_matchups_for_sport(
    all_subteams: dict[str, Subteam], sport: str
) -> list[tuple[Subteam, Subteam]]:
    """Determine matchups between the teams.

    Do this in a rotating round-robin fashion, where each team plays
    against each other team in the same subteam-pool.
    """
    all_subteams = {
        k: team for k, team in all_subteams.items() if sport in k and "R" not in k
    }
    num_teams = len(all_subteams)
    assert (
        num_teams % 3 == 0
    ), f"{sport}: Please provide equal amount of subteams for each team, found {num_teams}"
    teams_subteams = [
        [
            subteam
            for subteam in all_subteams.values()
            if subteam.main_team_letter == letter
        ]
        for letter in "ABC"
    ]

    return create_combinations(*teams_subteams)


def write_match_backup(matches: list[Match], overwrite=False):
    """Write a backup for the matches that were determined."""
    df = turn_series_list_to_dataframe([m.as_series for m in matches])
    fpath = FpathRegistry.all_matches
    if fpath.exists() and not overwrite:
        print("Skipped overwriting matches")
        return
    df.to_csv(fpath)
