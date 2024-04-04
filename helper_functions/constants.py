from dataclasses import dataclass
from pathlib import Path

# The path to the data folder
DATAPATH = Path(__file__).parent.parent / "data"
PAGESPATH = Path(__file__).parent.parent / "pages"

SPORTS_LIST = [
    "basketball",
    "running_sprints",
    "volleyball",
    "chess",
    "football",
    "tennis",
    "capture_the_flag",
    "spikeball",
    "beer_pong",
    "fooseball",
    "ping_pong",
]


@dataclass
class FpathRegistry:
    """Paths to some commonly used files."""

    all_responses = DATAPATH.joinpath("sanitized_responses.csv")
