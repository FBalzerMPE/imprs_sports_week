from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from .sport_location import SportLocation
from .streamlit_util import st_display_team_highlighted_table
from .util import read_event_desc


def generate_round_robin_list(
    teams: list[str], max_match_number=2
) -> list[tuple[str, str]]:
    """Generate a round-robin list of matches between the teams."""
    matches = []
    for team_1 in teams:
        for team_2 in teams:
            if team_1.split()[0] == team_2.split()[0]:
                continue
            match = (team_1, team_2)
            num_t1 = np.sum([team_1 in match for match in matches])
            num_t2 = np.sum([team_2 in match for match in matches])
            if (num_t1 < max_match_number) and (num_t2 < max_match_number):
                matches.append(match)
    return matches


def schedule_matches(teams: list[str], num_subteams: int, max_match_number=2):
    """Schedule matches between the teams.
    Do this in a round-robin fashion, where each team plays
    against each other team in the same sub-team-pool."""
    matches = []
    for subteam_key in "ABCDEFGH"[:num_subteams]:
        subteams = [team for team in teams if subteam_key in team]
        matches += generate_round_robin_list(subteams, max_match_number)
    if len(matches) == 0:
        matches = generate_round_robin_list(teams, max_match_number)
    return pd.DataFrame(matches, columns=["Team 1", "Team 2"])


@dataclass
class SportEvent:
    """Class representing the different types of sports events we are offering."""

    name: str
    """The name of the event."""

    start: datetime
    """The time and day this event starts."""

    end: datetime
    """The time and day this event ends."""

    match_duration: timedelta
    """The average duration of a single match for this sport."""

    loc: SportLocation
    """The location where this sport is taking place."""

    organizer_names: list[str]
    """The name of the person responsible for organizing this event."""

    icon: str
    """The emoji icon representing this sport."""

    min_player_val: int
    """The minimum number of players required in a big team for this sport."""

    num_players_per_subteam: int
    """The number of players per sub-team for this sport."""

    num_subteams: int = 1
    """The number of sub-teams for this sport."""

    num_pitches: int = 1
    """The number of pitches available for this sport."""

    num_matches_per_subteam: int = 2
    """The number of matches each sub-team will play."""

    conflicting_sports: list[str] = field(default_factory=list)

    sub_teams: dict[int, dict[str, pd.DataFrame]] = field(
        default_factory=dict, repr=False
    )
    """The sub-teams for this sport, mapping the team key to the sub-team keys with respective players."""

    desc: str = field(init=False, repr=False)
    """A description of what's going on during this event, in markdown format, including the rules."""

    days: list[str] = field(init=False)

    def __post_init__(self):
        assert self.start < self.end, "The start time must be before the end time."
        assert (
            self.num_matches_per_subteam
            * self.num_subteams
            / self.num_pitches
            * self.match_duration
            < self.end - self.start
        ), f"The {self.name} event is too short for the number of matches and sub-teams."
        self.desc = read_event_desc(self.sanitized_name)
        self.days = [
            day.strftime("%A").lower()
            for day in pd.date_range(self.start, self.end).date
        ]
        try:
            from .team_registry import ALL_TEAMS

            for team in ALL_TEAMS:
                self.sub_teams[team.team_index] = team.get_subteams_for_sport(self)
        except (KeyError, FileNotFoundError, ValueError, AssertionError):
            # print("No sub-teams initialized.")
            pass

    @property
    def sanitized_name(self) -> str:
        return self.name.replace(" ", "_").replace("/", "_").lower()

    @property
    def calendar_entry(self) -> dict[str, str | dict]:
        title = f"{self.name} (Contact: {', '.join(self.organizer_names)})"
        return {
            "title": title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),  # "2024-04-29T21:00:00",
            "resourceId": self.name,
            "extendedProps": {"url": "/" + self.sanitized_name},
        }

    @property
    def match_calendar_entries(self) -> list[dict[str, str | dict]]:
        """Get the calendar entries for the matches."""
        matches = self.matches()
        entries = []
        for i, match_ in matches.iterrows():
            title = f"{match_['Team 1']} vs {match_['Team 2']}"
            time = datetime.strptime(match_["Time"], "%H:%M").time()
            start = datetime.combine(self.start.date(), time)
            entries.append(
                {
                    "title": title,
                    "start": start.isoformat(),
                    "end": (start + self.match_duration).isoformat(),
                    "resourceId": self.name,
                    "color": "green",
                }
            )
        return entries

    @property
    def html_url(self) -> str:
        return f'<span style="white-space:nowrap;">{self.icon} <a href="/{self.name}" target="_self">{self.name}</a></span>'

    @property
    def short_info_text(self) -> str:
        contact_link = (
            f'<a href="/Contact" target="_self">{", ".join(self.organizer_names)}</a>'
        )
        text = f"""
- **Location:** {self.loc.titledName}
- **Time:** {self.start.strftime('%H:%M')} to {self.end.strftime('%H:%M')} on **{self.start.strftime('%A, %B %d')}**
- **Organizers:** {contact_link}"""
        return text

    @property
    def sub_team_df(self) -> pd.DataFrame:
        team_dict = {
            str(team_key) + " " + subteam_key: sorted(subteam["nickname"])
            for team_key, val in self.sub_teams.items()
            for subteam_key, subteam in val.items()
        }
        if not any("B" in team for team in team_dict.keys()):
            team_dict = {k.replace(" A", " "): v for k, v in team_dict.items()}

        rows = [[team_key] + players for team_key, players in team_dict.items()]
        subteams = pd.DataFrame(
            rows,
            columns=["Team"]
            + [f"Player {i+1}" for i in range(self.num_players_per_subteam)],
        )
        return subteams

    def get_attending_players(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.sanitized_name]]

    def matches(self) -> pd.DataFrame:
        teams = self.sub_team_df["Team"].tolist()

        # Generate the schedule
        schedule = schedule_matches(teams, self.num_subteams)
        courts = [
            str(i + 1)
            for _ in range(len(schedule) // self.num_pitches)
            for i in range(self.num_pitches)
        ]
        date_range = pd.date_range(
            start=self.start,
            periods=len(schedule),
            freq=self.match_duration,
        )
        dates = [
            date.strftime("%H:%M")
            for date in date_range
            for _ in range(self.num_pitches)
        ]
        schedule.insert(0, "Time", dates[: len(schedule)])
        schedule.insert(1, "Court", courts)

        return schedule

    def write_streamlit_rep(self):
        st.write(self.short_info_text, unsafe_allow_html=True)
        st.write(self.desc)
        st.write(f"## Schedule\n")
        st_display_team_highlighted_table(self.matches())

        st.write(f"## Sub-teams\n")
        st_display_team_highlighted_table(self.sub_team_df, full_row=True)
