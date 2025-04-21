from __future__ import annotations

import random
from functools import reduce
from typing import TYPE_CHECKING

import numpy as np

from ..classes.team import Team
from ..logger import LOGGER

if TYPE_CHECKING:
    from ..classes.sport_event import SportEvent
    from ..classes.subteam import Subteam


def _generate_subteams_for_sport(
    team: Team,
    sport: SportEvent,
    num_subteams: int | None = None,
    num_players_per_subteam: int | None = None,
    seed: int = 42,
) -> list[Subteam]:
    """Get a dictionary of subteams for a specific sport."""
    from ..classes.subteam import Subteam

    avail_players = team.get_all_players_for_sport(sport.sanitized_name)
    if num_subteams is None:
        num_subteams = sport.num_subteams
    if num_players_per_subteam is None:
        num_players_per_subteam = sport.num_players_per_subteam
    req_player_num = num_subteams * num_players_per_subteam
    assert req_player_num <= len(
        avail_players
    ), f"{sport.name}: Not enough players (only {len(avail_players)}) in the team to create the requested number of subteams (at least {req_player_num} expected)."
    conf_sports = sport.conflicting_sports
    is_in_collision = (
        reduce(
            lambda a, b: a & b,
            [avail_players[other_sport] for other_sport in conf_sports],
        )
        if len(conf_sports) > 0
        else np.zeros_like(avail_players["nickname"], dtype=bool)
    )
    # This relation for the weights seems to work out nicely.
    avail_players["weights"] = 2 / avail_players["num_sports"] + 5 * (~is_in_collision)

    subteams = []
    for i in range(num_subteams):
        subteam = avail_players.sample(
            num_players_per_subteam,
            replace=False,
            random_state=seed + i,
            weights=avail_players["weights"],
        )
        avail_players = avail_players.drop(subteam.index)
        subteam_key = (
            str(i + 1) if sport.sanitized_name != "ping_pong" else f"{i+1:0>2}"
        )
        subteams.append(
            Subteam(
                sport=sport.sanitized_name,
                main_team_letter=team.team_letter,
                sub_key=subteam_key,
                players=subteam["nickname"].tolist(),
            )
        )
    subteams.append(
        Subteam(
            sport=sport.sanitized_name,
            main_team_letter=team.team_letter,
            sub_key="R",
            players=avail_players["nickname"].tolist(),
        )
    )
    return subteams


def _get_all_players_for_sport(
    all_subteams: list[Subteam],
    sport: str,
    no_reserve: bool = True,
    reserve_only: bool = False,
) -> list[str]:
    """Get all players in the team that are available for a specific sport."""
    assert (
        not reserve_only or not no_reserve
    ), "You cannot set both reserve_only and no_reserve to True."
    sport_subteams = [subteam for subteam in all_subteams if subteam.sport == sport]
    return [
        player
        for subteam in sport_subteams
        for player in subteam.players
        if (no_reserve and not subteam.is_reserve)
        or (reserve_only and subteam.is_reserve)
    ]


def _resolve_subteams_conflict(all_subteams: list[Subteam], sport_a: str, sport_b: str):
    teams_a = [subteam for subteam in all_subteams if subteam.sport == sport_a]
    teams_b = [subteam for subteam in all_subteams if subteam.sport == sport_b]
    all_players_a = _get_all_players_for_sport(teams_a, sport_a, no_reserve=True)
    all_players_b = _get_all_players_for_sport(teams_b, sport_b, no_reserve=True)
    reserve_players_a = _get_all_players_for_sport(
        teams_a, sport_a, reserve_only=True, no_reserve=False
    )
    reserve_players_b = _get_all_players_for_sport(
        teams_b, sport_b, reserve_only=True, no_reserve=False
    )
    # As we do not want to create new doubled reserve players, we need to remove them from further considerations
    for player in all_players_a:
        if player in reserve_players_b:
            reserve_players_b.remove(player)
    for player in all_players_b:
        if player in reserve_players_a:
            reserve_players_a.remove(player)
    player_intersect = set(all_players_a).intersection(all_players_b)
    initial_reserve_intersect = set(reserve_players_a).intersection(reserve_players_b)
    LOGGER.debug(
        f"\n\t{sport_a}: {all_players_a}\n\t{sport_b}: {all_players_b}\n\tIntersect: {player_intersect}\n\tReserve Intersect: {initial_reserve_intersect}"
    )
    for player in player_intersect:
        reserve_intersect = set(reserve_players_a).intersection(reserve_players_b)
        # If there are players that are set for reserve in both, replace one of the slots
        subteam_a = [subteam for subteam in teams_a if player in subteam.players][0]
        subteam_b = [subteam for subteam in teams_b if player in subteam.players][0]
        reserve_a = [subteam for subteam in teams_a if subteam.is_reserve][0]
        reserve_b = [subteam for subteam in teams_b if subteam.is_reserve][0]
        if len(reserve_intersect) > 0:
            switch_player = random.choice(list(reserve_intersect))
            subteam_b.switch_player_with_other(player, switch_player, reserve_b)
            reserve_players_b.remove(switch_player)
            if switch_player in reserve_players_a:
                reserve_players_a.remove(switch_player)
        # If no double-reserve players are available, try to switch in some reserve player for team b
        elif len(reserve_players_b) > 0:
            switch_player = random.choice(reserve_players_b)
            subteam_b.switch_player_with_other(player, switch_player, reserve_b)
            reserve_players_b.remove(switch_player)
        # Oherwise, try the same for team a:
        elif len(reserve_players_a) > 0:
            switch_player = random.choice(reserve_players_a)
            subteam_a.switch_player_with_other(player, switch_player, reserve_a)
            reserve_players_a.remove(switch_player)
        else:
            LOGGER.warning(
                f"No solution found for {player}, they are currently double-booked for {sport_a} and {sport_b}."
            )
    reserve_intersect = set(reserve_players_a).intersection(reserve_players_b)
    if len(reserve_intersect) > 0:
        LOGGER.warning(
            f"The following players are still set as reserve for both {sport_a} and {sport_b}: {reserve_intersect}"
        )


def generate_all_subteams(team: Team, seed=42) -> list[Subteam]:
    """Generate all necessary subteams for the given team.

    Try to solve conflicts for players being doubly subscribed.
    """
    from ..data_registry import DATA_NOW

    random.seed(seed)
    all_subteams: list[Subteam] = []
    for sport in DATA_NOW.sport_events.values():
        subteams = _generate_subteams_for_sport(team, sport)
        all_subteams += subteams
    # Shift players that are in subteams for both, and try to replace them with reservists
    for colliding_pairs in [
        ["volleyball", "basketball"],
        ["basketball", "running_sprints"],
        ["volleyball", "running_sprints"],
        ["football", "tennis"],
        ["badminton", "spikeball"],
        ["capture_the_flag", "chess"],
        ["foosball", "beer_pong"],
    ]:
        _resolve_subteams_conflict(all_subteams, *colliding_pairs)
    return all_subteams


def try_switch_players(
    name_1: str, name_2: str, sport: str, all_subteams: list[Subteam]
):
    subteams = [
        subteam
        for subteam in all_subteams
        if subteam.sport == sport
        and (name_1 in subteam.players or name_2 in subteam.players)
    ]

    if len(subteams) < 2:
        return
    subteam_1 = [subteam for subteam in subteams if name_1 in subteam.players][0]
    subteam_2 = [subteam for subteam in subteams if name_2 in subteam.players][0]
    subteam_1.switch_player_with_other(name_1, name_2, subteam_2)
