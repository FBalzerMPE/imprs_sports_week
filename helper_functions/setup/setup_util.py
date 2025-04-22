from typing import TYPE_CHECKING

import pandas as pd

from ..constants import DATAPATH, FpathRegistry

if TYPE_CHECKING:
    from ..classes.team import Team


def get_real_player_name(nickname: str, first_name_only: bool = True) -> str:
    """Try to retrieve this player's real name from the hidden data."""
    try:
        clear_names = FpathRegistry.get_hidden_responses().set_index(
            "nickname", drop=False
        )
    except FileNotFoundError:
        return nickname
    name = clear_names["name"].to_dict().get(nickname, "")
    email_suffix = ", " + clear_names["email"].to_dict().get(nickname, "")
    if not first_name_only:
        return name + email_suffix
    first_name = name.split()[0]
    last_name = name.split()[-1] if len(name.split()) > 1 else ""
    first_names = [n.split()[0] for n in clear_names["name"]]
    if (
        first_names.count(first_name) > 1 and last_name
    ):  # If the first name is not unique and there is a last name
        return (
            first_name + " " + last_name[0] + email_suffix
        )  # Return the first name and the first letter of the last name
    else:
        return first_name + email_suffix


def update_player_signup_status(
    teams: list["Team"], player_name: str, sport: str, status: bool
) -> None:
    """Update the signup status of a player."""
    for team in teams:
        team.change_player_attribute(player_name, sport, status, not_exist_okay=True)
