from dataclasses import dataclass
from pathlib import Path

from PIL import Image

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

    all_matches = DATAPATH.joinpath("matches.csv")

    @staticmethod
    def get_animal_pic_path(animal_name: str) -> str:
        """Retrieves the animal pic path relative to the top level path."""
        name = animal_name.lower().replace(" ", "_")
        return str(f"app/static/animal_pics/small_size/{name}.png")
