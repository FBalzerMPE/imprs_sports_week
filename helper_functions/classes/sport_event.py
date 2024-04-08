from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import FpathRegistry
from ..data_registry import ALL_MATCHES, ALL_SUBTEAMS
from ..streamlit_util import st_style_df_with_team_vals
from ..util import read_event_desc, turn_series_list_to_dataframe
from .match import Match
from .sport_location import SportLocation
from .subteam import Subteam


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
    """The other sports overlapping with this one."""

    subteams: list[Subteam] = field(default_factory=list, repr=False)
    """The sub-teams for this sport."""

    matches: list[Match] = field(default_factory=list, repr=False)
    """All matches scheduled for this sport."""

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
            if day.strftime("%A").lower() != "wednesday"
        ]
        self.subteams = [
            subteam for subteam in ALL_SUBTEAMS if subteam.sport == self.sanitized_name
        ]
        self.matches = [m for m in ALL_MATCHES if m.sport == self.sanitized_name]

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
    def match_calendar_entries(self) -> list[dict[str, str]]:
        """Get the calendar entries for the matches."""
        return [match_.get_calendar_entry() for match_ in self.matches]

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
        return turn_series_list_to_dataframe([team.as_series for team in self.subteams])

    @property
    def match_df(self) -> pd.DataFrame:
        return turn_series_list_to_dataframe([m.as_series for m in self.matches])

    def get_attending_players(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.sanitized_name]]

    def _st_display_matches(self):
        df = self.match_df.fillna("")
        for col in ["location", "day"]:
            if len(np.unique(df[col])) == 1:
                df = df.drop(columns=col)

        column_configs = {}
        column_configs["time"] = st.column_config.Column("Time")
        column_configs["team_a"] = st.column_config.TextColumn("Team a", width="small")
        column_configs["team_b"] = st.column_config.TextColumn("Team b", width="small")
        column_configs["result"] = st.column_config.Column("Result", width="small")
        column_configs["winner"] = st.column_config.Column("Winner", width="small")
        style = st_style_df_with_team_vals(df)
        st.dataframe(
            style,
            hide_index=True,
            column_config=column_configs,
            column_order=[
                "day",
                "time",
                "location",
                "team_a",
                "team_b",
                "result",
                "winner",
            ],
        )

    def _st_display_subteams(self):
        df = self.sub_team_df
        df = df.sort_values(["is_reserve", "full_key"], ascending=[True, True])
        column_configs = {"full_key": st.column_config.Column("Subteam", width="small")}
        for i in range(max(df["players"].apply(len))):
            df[f"avatar_{i}"] = df["players"].apply(
                lambda x: FpathRegistry.get_animal_pic_path(x[i]) if i < len(x) else ""
            )
            column_configs[f"avatar_{i}"] = st.column_config.ImageColumn("")
        st.dataframe(
            st_style_df_with_team_vals(df, full_row=True),
            hide_index=True,
            column_config=column_configs,
            column_order=[*column_configs, "players"],
        )

    def write_streamlit_rep(self):
        st.write(self.short_info_text, unsafe_allow_html=True)
        st.write(self.desc)
        st.write(f"## Schedule\n")
        self._st_display_matches()

        st.write(f"## Sub-teams\n")
        self._st_display_subteams()
