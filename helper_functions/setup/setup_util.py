import pandas as pd

from ..constants import DATAPATH


def get_real_player_name(nickname: str, first_name_only: bool = True) -> str:
    """Try to retrieve this player's real name from the hidden data."""
    clear_names = pd.read_csv(DATAPATH.joinpath("hidden/nickname_to_name.csv"))
    name = clear_names.set_index("nickname")["name"].to_dict().get(nickname, "")
    if not first_name_only:
        return name
    first_name = name.split()[0]
    last_name = name.split()[1] if len(name.split()) > 1 else ""
    first_names = [n.split()[0] for n in clear_names["name"]]
    if (
        first_names.count(first_name) > 1 and last_name
    ):  # If the first name is not unique and there is a last name
        return (
            first_name + " " + last_name[0]
        )  # Return the first name and the first letter of the last name
    else:
        return first_name
