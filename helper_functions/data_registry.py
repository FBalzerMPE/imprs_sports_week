"""Module where we load the data necessary for the module to operate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd
import streamlit as st
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
        except FileNotFoundError:
            LOGGER.info("Couldn't load team", i)
            pass
    return teams


# @st.cache_data(ttl=60)
def get_players(
    from_teams: bool = True, year=CURRENT_YEAR, modification_time: str = ""
) -> pd.DataFrame:
    """Loads a dataframe of all players."""
    teams = get_teams(year)
    if from_teams:
        if len(teams) > 0:
            return pd.concat([team.player_df for team in teams])
        else:
            LOGGER.info(
                "No teams found to get the players from. Trying to revert to the response sheet."
            )
    return pd.read_csv(FpathRegistry.get_path_responses(year))


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

                all_subteams[sport + "_" + subteam.short_key] = subteam
    if year != 2025:
        return all_subteams
    for num, sport in zip((12, 5), ("volleyball", "basketball")):
        for i in range(num):
            for team in "ABC":
                subteam = Subteam(sport, team, str(i + 1), [])
                all_subteams[sport + "_" + subteam.short_key] = subteam
    return all_subteams


# @st.cache_data(ttl=60)
def get_match_df(year=CURRENT_YEAR, modification_time: str = "") -> pd.DataFrame:
    # Use the modification time to check if the file has changed
    fpath = FpathRegistry.get_path_matches(year)
    if not fpath.exists():
        return pd.DataFrame()
    match_df = pd.read_csv(fpath)
    match_df["start"] = pd.to_datetime(match_df["start"])
    return match_df.infer_objects(copy=True).fillna("")  # type: ignore


def get_matches(year=CURRENT_YEAR, silent: bool = False) -> list[Match]:
    mod_time = str(FpathRegistry.get_path_matches(year).stat().st_mtime)
    match_df = get_match_df(year, modification_time=mod_time)
    subteams = get_subteams(year)
    match_list = []
    for _, match_ in match_df.iterrows():
        match_list.append(Match.from_dataframe_entry(match_, subteams, silent))
        # except KeyError as e:
        #     if not warn:
        #         continue
        #     LOGGER.warning(
        #         f"Couldn't load {match_["full_key"]}.\n\t{match_["team_a"]} vs {match_["team_b"]} at {match_["start"]}."
        #     )
    return match_list


def load_sport_locations() -> dict[str, SportLocation]:
    locs = yaml.safe_load(FpathRegistry.sport_locations.read_text())
    return {loc["key"]: SportLocation(**loc) for loc in locs}


def load_organizers(year=CURRENT_YEAR) -> dict[str, SportsOrganizer]:
    fpath = FpathRegistry.get_path_sports_organizers(year)
    orgs = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    orgs = sorted(
        orgs,
        key=lambda x: ("0" if x.get("is_committee_member", False) else "1")
        + ("0" if len(x.get("sport_keys")) > 0 else "1")
        + x["name"],
    )
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

        mod_time = str(FpathRegistry.get_path_responses(year).stat().st_mtime)
        players = get_players(year=year, modification_time=mod_time)
        subteams = get_subteams(year)
        matches = get_matches(year)
        mod_time = str(FpathRegistry.get_path_matches(year).stat().st_mtime)
        match_df = get_match_df(year, modification_time=mod_time)
        organizers = load_organizers(year)
        return cls(year, teams, players, subteams, matches, match_df, organizers)

    @property
    def path(self) -> Path:
        return DATAPATH.joinpath(str(self.year))

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
        """The start date of the sports week."""
        return self.sport_events["ping_pong"].start.date()

    @property
    def end_date(self) -> date:
        """The end date of the sports week."""
        return self.sport_events["ping_pong"].end.date()

    @property
    def days(self) -> list[date]:
        """The days the sports week of this year takes place at"""
        return [
            self.start_date + timedelta(days=i)
            for i in range((self.end_date - self.start_date).days + 1)
        ]

    @property
    def nickname_to_name_df(self) -> pd.DataFrame:
        fpath = FpathRegistry.get_path_hidden(self.year).joinpath(
            "nickname_to_name.csv"
        )
        if not fpath.exists():
            LOGGER.warning(f"Couldn't find nickname to name file at {fpath}")
            return pd.DataFrame()
        return pd.read_csv(fpath)

    def get_day(
        self, day: Literal["monday", "tuesday", "wednesday", "thursday", "friday"]
    ) -> date:
        """Get the date of the sports week for a specific day."""
        day_idx = ["monday", "tuesday", "wednesday", "thursday", "friday"].index(day)
        return self.days[day_idx]

    def get_running_sprints_score(self, team_letter: str) -> float:
        """Return the score for the running sprints event."""
        # Maybe TODO: Read this stuff from some sort of file.
        year_dict: dict[int, dict[str, int]] = {
            2024: {"B": 35, "C": 34, "A": 31},
            2025: {"A": 18, "B": 46, "C": 36},
        }
        return year_dict[self.year].get(team_letter, 0)

    def get_team(self, team_letter: str) -> Team:
        """Get a team by its letter."""
        team_letter = team_letter.replace("Team ", "").upper()
        for team in self.teams:
            if team.team_letter == team_letter:
                return team
        raise KeyError(f"Team {team_letter} not found.")

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

    def reload(self):
        """Reloads the data from disk if it has updated."""
        self.teams = get_teams(self.year)
        self.players = get_players(year=self.year)
        self.subteams = get_subteams(self.year)
        self.matches = get_matches(self.year, silent=True)
        self.match_df = get_match_df(self.year)
        self.organizers = load_organizers(self.year)
        self.load_sport_events()

    def get_hidden_feedback_info(self) -> dict[str, dict[str, Any]]:
        fpath = FpathRegistry.get_path_hidden(self.year).joinpath("feedback_info.yml")
        if not fpath.exists():
            LOGGER.warning(f"No feedback file found for {self.year}")
            return {}
        ftext = fpath.read_text(encoding="utf-8")
        return {v["name"]: v for v in yaml.safe_load(ftext)}


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
