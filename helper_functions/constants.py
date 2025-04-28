from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

import pandas as pd

# The path to the data folder
DATAPATH = Path(__file__).parent.parent / "data"
PAGESPATH = Path(__file__).parent.parent / "pages"
CURRENT_YEAR: Final[int] = 2025

SPORTS_LIST = [
    "ping_pong",
    "basketball",
    "running_sprints",
    "volleyball",
    "football",
    "tennis",
    "badminton",
    "spikeball",
    "capture_the_flag",
    "chess",
    "beer_pong",
    "foosball",
]


ALL_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]


@dataclass
class FpathRegistry:
    """Paths to some commonly used files."""

    sport_locations = DATAPATH.joinpath("assets/sport_locations.yml")
    project_changelog = DATAPATH.joinpath("assets/changelog.yml")

    @staticmethod
    def get_path_matches(year=CURRENT_YEAR) -> Path:
        """The path for the match dataframe of the given year."""
        return DATAPATH.joinpath(f"{year}/matches.csv")

    @staticmethod
    def get_path_changelog(year=CURRENT_YEAR) -> Path:
        """The path for the changelog text file of the given year."""
        return DATAPATH.joinpath(f"{year}/changelog.md")

    @staticmethod
    def get_path_sport_events(year=CURRENT_YEAR) -> Path:
        """The path for the sport event dataframe of the given year."""
        return DATAPATH.joinpath(f"{year}/sport_events.yml")

    @staticmethod
    def get_path_sports_organizers(year=CURRENT_YEAR) -> Path:
        """The path for the sports organizer dataframe of the given year."""
        return DATAPATH.joinpath(f"{year}/sports_organizers.yml")

    @staticmethod
    def get_path_responses(year=CURRENT_YEAR, sanitized=True, latest=False) -> Path:
        if sanitized:
            return DATAPATH.joinpath(f"{year}/sanitized_responses.csv")
        p = DATAPATH.joinpath(f"{year}/hidden/processed_responses.csv")
        if not latest:
            return p
        files = sorted(
            p.parent.glob("form_responses_*.csv"), key=lambda p: p.stat().st_birthtime
        )
        assert (
            len(files) > 0
        ), f"Couldn't find any form response files, make sure to add them in the 'hidden' directory for {year}."
        return files[-1]

    @staticmethod
    def get_path_team(letter: str, year=CURRENT_YEAR) -> Path:
        """The Path for the given team's dataframe."""
        return DATAPATH.joinpath(f"{year}/teams/team_{letter}.csv")

    @staticmethod
    def get_path_hidden(year=CURRENT_YEAR) -> Path:
        """The Path for the hidden stuff for this year."""
        return DATAPATH.joinpath(f"{year}/hidden")

    @staticmethod
    def get_path_running_sprints(year=CURRENT_YEAR) -> Path:
        """The path to the results of the running/sprints event"""
        return DATAPATH.joinpath(f"{year}/running_sprints_results.md")

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
        institute = institute.lower().replace("/lmu", "")
        return str(DATAPATH.joinpath(f"assets/institute_logos/{institute}.png"))

    @staticmethod
    def get_sport_info_path(
        sport: str,
        info_type: Literal["introduction", "rules", "specifications", "advanced_rules"],
    ) -> Path:
        return DATAPATH.joinpath(f"sport_descriptions/{sport}/{info_type}.md")

    @staticmethod
    def get_sport_pic_path(sport: str) -> str:
        """Retrieves the animal pic path relative to the top level path."""
        sport = sport.lower().replace(" ", "_")
        return str(DATAPATH.joinpath(f"assets/sports_pics/{sport}.png"))

    @staticmethod
    def get_hidden_responses(year=CURRENT_YEAR) -> pd.DataFrame:
        """Reads the hidden responses from the file."""
        fpath = FpathRegistry.get_path_responses(year, sanitized=False)
        if not fpath.exists():
            raise FileNotFoundError(f"File {fpath} does not exist.")
        return pd.read_csv(fpath)
