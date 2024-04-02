from pathlib import Path
import pandas as pd
import numpy as np


# The path to the data folder
DATAPATH = Path(__file__).parent.parent / "data"

_sports_names = [
    "Basketball",
    "Beer Pong",
    "Capture the flag",
    "Chess",
    "Fooseball",
    "Football",
    "Ping Pong",
    "Running/Sprints",
    "Spikeball",
    "Tennis",
    "Volleyball",
]
# The minimum amount of players we require for each sport, important for building the teams
_min_sports_values = [8, 6, 8, 3, 4, 11, 4, 3, 4, 4, 8]


# The sports we support
SPORTS_DF = pd.DataFrame(
    np.array([_sports_names, _min_sports_values]).T, columns=["proper_name", "min_val"]
)
SPORTS_DF["min_val"] = SPORTS_DF["min_val"].astype(int)
SPORTS_DF["name"] = "does_" + SPORTS_DF["proper_name"].str.lower().str.replace(" ", "_")

