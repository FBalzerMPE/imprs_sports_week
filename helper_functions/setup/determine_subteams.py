from functools import reduce

from ..sport_event import SportEvent
import pandas as pd
from ..team import Team


def get_subteams_for_sport(
    team: Team,
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
    avail_players = team.get_all_players_for_sport(
        sport.sanitized_name, [f"avail_{day.lower()}" for day in sport.days]
    )
    req_player_num = num_subteams * num_players_per_subteam
    assert req_player_num <= len(
        avail_players
    ), f"Not enough players (only {len(avail_players)}) in the team to create the requested number of subteams (at least {req_player_num} expected)."
    assert num_subteams <= 8, "We only support up to 8 subteams."

    is_in_collision = reduce(
        lambda a, b: a & b,
        [avail_players[other_sport] for other_sport in sport.conflicting_sports],
    )
    avail_players["weights"] = 2 / avail_players["num_sports"] + 5 * (
        ~is_in_collision
    )
    # is_priority = avail_players["num_sports"] == 1
    # prio_sample = avail_players[is_priority]
    # is_in_collision = reduce(
    #     lambda a, b: a & b,
    #     [avail_players[other_sport] for other_sport in sport.conflicting_sports],
    # )
    # midprio_sample = avail_players[~is_priority & ~is_in_collision]
    # nonprio_sample = avail_players[~is_priority & is_in_collision]
    subteams = {}
    for i in range(num_subteams):
        subteam = avail_players.sample(
            num_players_per_subteam,
            random_state=seed + i,
            weights=avail_players["weights"],
        )
        avail_players = avail_players.drop(subteam.index)
        # First, sample as many players from the prio sample.
        # if len(prio_sample) < num_players_per_subteam:
        #     subteam = prio_sample
        #     prio_sample = prio_sample.drop(subteam.index)
        # else:
        #     subteam = prio_sample.sample(
        #         num_players_per_subteam, replace=False, random_state=seed + i
        #     )
        #     prio_sample = prio_sample.drop(subteam.index)
        # # Then, fill up with non-priority players.
        # num_remaining = num_players_per_subteam - len(subteam)
        # fill_players = nonprio_sample.sample(
        #     num_remaining, replace=False, random_state=seed + i
        # )
        # nonprio_sample = nonprio_sample.drop(fill_players.index)
        subteams["ABCDEFGH"[i]] = subteam  # pd.concat([subteam, fill_players])
    for player in team._players:  # TODO: Change this.
        team_key = {
            k
            for k, team in subteams.items()
            if player["nickname"] in team["nickname"].tolist()
        }
        key = "" if len(team_key) == 0 else team_key.pop()
        if player["nickname"] in avail_players["nickname"].tolist():
            key = "R"
        player[f"subteam_{sport.sanitized_name}"] = key
    return subteams