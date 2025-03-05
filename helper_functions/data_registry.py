"""Module where we load the data necessary for the module to operate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

import pandas as pd
import yaml

from .classes.match import Match
from .classes.sport_location import SportLocation
from .classes.sports_organizer import SportsOrganizer
from .classes.subteam import Subteam
from .classes.team import Team
from .constants import CURRENT_YEAR, DATAPATH, SPORTS_LIST, FpathRegistry
from .logger import LOGGER

if TYPE_CHECKING:
    from .classes.sport_event import SportEvent

# import streamlit as st


# @st.cache_data
def get_teams(year=CURRENT_YEAR) -> list[Team]:
    """Get the teams from the backup files."""
    teams = []
    num_teams = len(list(DATAPATH.joinpath(f"{year}/teams/").glob("*.csv")))
    for i in range(num_teams):
        try:
            teams.append(Team.from_backup(i, year))
        except (FileNotFoundError, KeyError):
            LOGGER.info("Couldn't load team", i)
            pass
    return teams


# @st.cache_data
def get_players(from_teams: bool = True, year=CURRENT_YEAR) -> pd.DataFrame:
    """Loads a dataframe of all players."""
    teams = get_teams(year)
    if from_teams:
        if len(teams) > 0:
            return pd.concat([team.player_df for team in teams])
        else:
            LOGGER.warning(
                "No teams found to get the players from. Trying to revert to the response sheet."
            )
    return pd.read_csv(FpathRegistry.get_path_responses(year))


# @st.cache_data
def get_subteams(year=CURRENT_YEAR) -> dict[str, Subteam]:
    all_subteams = {}
    for team in get_teams(year):
        df = team.player_df
        for sport in SPORTS_LIST:
            if sport not in df.columns:
                continue
            column = df[f"subteam_{sport}"]
            for team_key in column[column.notna()].unique():
                players = df[column == team_key]["nickname"].tolist()
                if sport == "ping_pong":
                    team_key = (
                        f"{team_key:0>2}" if team_key != "R" else team_key
                    )  # Ensure we load it in as string
                subteam = Subteam(
                    sport,
                    main_team_letter=team.team_letter,
                    sub_key=team_key,
                    players=players,
                )
                all_subteams[sport + "_" + subteam.full_key] = subteam
    return all_subteams


# @st.cache_data
def get_match_df(year=CURRENT_YEAR) -> pd.DataFrame:
    fpath = FpathRegistry.get_path_matches(year)
    if not fpath.exists():
        return pd.DataFrame()
    match_df = pd.read_csv(fpath)
    match_df["start"] = pd.to_datetime(match_df["start"])
    return match_df.infer_objects(copy=True).fillna("")  # type: ignore


# @st.cache_data
def get_matches(year=CURRENT_YEAR) -> list[Match]:
    match_df = get_match_df(year)
    subteams = get_subteams(year)
    match_list = []
    for _, match_ in match_df.iterrows():
        try:
            match_list.append(Match.from_dataframe_entry(match_, subteams))
        except KeyError:
            LOGGER.info(
                f"Couldn't load {match_["full_key"]}.\n\t{match_["team_a"]} vs {match_["team_b"]}"
            )

    return match_list


def load_sport_locations() -> dict[str, SportLocation]:
    locs = yaml.safe_load(FpathRegistry.sport_locations.read_text())
    return {loc["key"]: SportLocation(**loc) for loc in locs}


def load_organizers(year=CURRENT_YEAR) -> dict[str, SportsOrganizer]:
    fpath = FpathRegistry.get_path_sports_organizers(year)
    orgs = yaml.safe_load(fpath.read_text())
    orgs = sorted(orgs, key=lambda x: x["name"])
    return {org["name"]: SportsOrganizer(**org, year=year) for org in orgs}


@dataclass
class DataRegistry:
    """Data registry to hold all data in one place."""

    year: int
    teams: list[Team]
    players: pd.DataFrame
    subteams: dict[str, Subteam]
    matches: list[Match]
    match_df: pd.DataFrame
    organizers: dict[str, SportsOrganizer]
    sport_events: dict[str, SportEvent] = field(init=False)

    @classmethod
    def from_year(cls, year=CURRENT_YEAR) -> "DataRegistry":
        teams = get_teams(year)
        players = get_players(year=year)
        subteams = get_subteams(year)
        matches = get_matches(year)
        match_df = get_match_df(year)
        organizers = load_organizers(year)
        return cls(year, teams, players, subteams, matches, match_df, organizers)

    @property
    def avail_sports(self) -> list[str]:
        return [sport.sanitized_name for sport in self.sport_events.values()]

    @property
    def team_letters(self) -> list[str]:
        return [team.team_letter for team in self.teams]

    @property
    def has_teams(self) -> bool:
        """Whether there are teams in the data registry."""
        return len(self.teams) > 0 and all([len(team) > 0 for team in self.teams])

    @property
    def has_scores(self) -> bool:
        """Whether there are scores in the data registry."""
        return len(self.teams) > 0 and any(self.match_df["winner"].notna())

    @property
    def start_date(self) -> date:
        return self.sport_events["ping_pong"].start.date()

    @property
    def end_date(self) -> date:
        return self.sport_events["ping_pong"].end.date()

    def get_running_sprints_score(self, team_letter: str) -> float:
        """Return the score for the running sprints event."""
        # Maybe TODO: Read this stuff from some sort of file.
        year_dict: dict[int, dict[str, int]] = {
            2024: {"B": 35, "C": 34, "A": 31},
            2025: {},
        }
        return year_dict[self.year].get(team_letter, 0)

    def load_sport_events(self):
        from .classes.sport_event import SportEvent

        fpath = FpathRegistry.get_path_sport_events(self.year)
        events = yaml.safe_load(fpath.read_text(encoding="utf-8"))
        self.sport_events = {
            (
                e := SportEvent.from_dict(event, ALL_LOCATIONS, self.organizers)
            ).sanitized_name: e
            for event in events
        }


ALL_LOCATIONS = load_sport_locations()
DATA_2024 = DataRegistry.from_year(2024)
DATA_NOW = DataRegistry.from_year(CURRENT_YEAR)


def get_data_for_year(year: int) -> DataRegistry:
    """Get the data for a specific year."""
    assert year in [2024, 2025], f"Year {year} not supported."
    return {2024: DATA_2024, 2025: DATA_NOW}[year]


# The weird way of loading the sport events is due to the fact that we need to load them
# after the data registries have been created.
DATA_2024.load_sport_events()
DATA_NOW.load_sport_events()
