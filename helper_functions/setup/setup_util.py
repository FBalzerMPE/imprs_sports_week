import pandas as pd
from ..constants import DATAPATH


def get_real_player_name(nickname: str, first_name_only: bool = True) -> str:
    """Try to retrieve this player's real name from the hidden data."""
    clear_names = pd.read_csv(
        DATAPATH.joinpath("hidden/nickname_to_name.csv"), index_col=0
    )
    name = clear_names.set_index("nickname")["name"].to_dict().get(nickname, "")
    return name.split()[0] if first_name_only else name
