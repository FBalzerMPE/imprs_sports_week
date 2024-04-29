from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import pandas as pd

# The path to the data folder
DATAPATH = Path(__file__).parent.parent / "data"
PAGESPATH = Path(__file__).parent.parent / "pages"

SPORTS_LIST = [
    "ping_pong",
    "basketball",
    "running_sprints",
    "volleyball",
    "chess",
    "football",
    "tennis",
    "capture_the_flag",
    "spikeball",
    "beer_pong",
    "foosball",
]


ALL_DAYS = ["monday", "tuesday", "thursday", "friday"]


@dataclass
class FpathRegistry:
    """Paths to some commonly used files."""

    processed_responses = DATAPATH.joinpath("hidden/processed_responses.csv")

    all_responses = DATAPATH.joinpath("sanitized_responses.csv")

    all_matches = DATAPATH.joinpath("matches.csv")

    @staticmethod
    def get_animal_pic_path(animal_name: str, from_static: bool = True) -> str:
        """Retrieves the animal pic path relative to the top level path."""
        name = animal_name.lower().replace(" ", "_")
        static_path = f"static/animal_pics/small_size/{name}.png"
        if from_static:
            return str(f"app/{static_path}")
        return str(DATAPATH.parent.joinpath(static_path))

    @staticmethod
    def get_institute_pic_path(institute: str) -> str:
        """Retrieves the animal pic path relative to the top level path."""
        institute = institute.lower()
        return str(DATAPATH.joinpath(f"assets/institute_logos/{institute}.png"))

    @staticmethod
    def get_sport_info_path(
        sport: str,
        info_type: Literal["introduction", "rules", "specifications", "advanced_rules"],
    ) -> Path:
        return DATAPATH.joinpath(f"sport_descriptions/{sport}/{info_type}.md")

    @staticmethod
    def get_hidden_responses() -> pd.DataFrame:
        """Reads the hidden responses from the file."""
        return pd.read_csv(FpathRegistry.processed_responses)
