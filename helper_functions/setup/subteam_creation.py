from functools import reduce

import numpy as np
import pandas as pd

from ..classes.sport_event import SportEvent
from ..classes.subteam import Subteam
from ..classes.team import Team


def generate_subteams_for_sport(
    team: Team,
    sport: SportEvent,
    num_subteams: int | None = None,
    num_players_per_subteam: int | None = None,
    seed: int = 42,
) -> list[Subteam]:
    """Get a dictionary of subteams for a specific sport."""
    avail_players = team.get_all_players_for_sport(
        sport.sanitized_name, [f"avail_{day.lower()}" for day in sport.days]
    )
    if num_subteams is None:
        num_subteams = sport.num_subteams
    if num_players_per_subteam is None:
        num_players_per_subteam = sport.num_players_per_subteam
    req_player_num = num_subteams * num_players_per_subteam
    assert req_player_num <= len(
        avail_players
    ), f"Not enough players (only {len(avail_players)}) in the team to create the requested number of subteams (at least {req_player_num} expected)."
    assert num_subteams <= 8, "We only support up to 8 subteams."
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
        subteams.append(
            Subteam(
                sport=sport.sanitized_name,
                main_team_letter=team.team_letter,
                sub_key=str(i + 1),
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
