from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd
import streamlit as st

from .constants import DATAPATH
from .sport_location import SportLocation


def read_event_desc(event_name: str) -> str:
    fpath = DATAPATH.joinpath(f"sport_descriptions/{event_name}.md")
    if not fpath.exists():
        print("File not found:", fpath)
        return "NO DESCRIPTION FOUND"
    with fpath.open() as f:
        return f.read()


@dataclass
class SportEvent:
    """Class representing the different types of sports events we are offering."""

    name: str
    """The name of the event."""

    start: datetime
    """The time and day this event starts."""

    end: datetime
    """The time and day this event ends."""

    loc: SportLocation
    """The location where this sport is taking place."""

    organizer_names: list[str]
    """The name of the person responsible for organizing this event."""

    icon: str
    """The emoji icon representing this sport."""

    min_player_val: int
    """The minimum number of players required in a big team for this sport."""

    sub_teams: dict[str, dict[str, pd.DataFrame]] = field(default_factory=dict)
    """The sub-teams for this sport, if it's a team sport."""

    desc: str = field(init=False, repr=False)
    """A description of what's going on during this event, in markdown format, including the rules."""

    days: list[str] = field(init=False)

    def __post_init__(self):
        assert self.start < self.end, "The start time must be before the end time."
        self.desc = read_event_desc(self.sanitized_name)
        self.days = [
            day.strftime("%A") for day in pd.date_range(self.start, self.end).date
        ]

    @property
    def sanitized_name(self) -> str:
        return self.name.replace(" ", "_").replace("/", "_").lower()

    @property
    def df_key(self) -> str:
        """The key for players in the dataframe, whether they attend this sport."""
        return "does_" + self.sanitized_name

    @property
    def calendar_entry(self) -> dict[str, str]:
        title = f"{self.name} (Contact: {', '.join(self.organizer_names)})"
        return {
            "title": title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),  # "2024-04-29T21:00:00",
            "resourceId": self.name,
        }

    @property
    def short_info_text(self) -> str:
        text = f"""# {self.name} {self.icon}
- **Location:** {self.loc.titledName}
- **Time:** {self.start.strftime('%H:%M')} to {self.end.strftime('%H:%M')} on **{self.start.strftime('%A, %B %d')}**
- **Organizers:** {', '.join(self.organizer_names)}"""
        return text

    def get_attending_players(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.df_key]]

    def write_streamlit_rep(self):
        st.write(self.short_info_text)
        st.write(self.desc)


SPORTS_EVENTS = {
    # Monday events
    "Volleyball": SportEvent(
        name="Volleyball",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        loc=SportLocation.tum_courts,
        organizer_names=["Benny", "Fabi"],
        icon=":volleyball:",
        min_player_val=8,
    ),
    "Running/Sprints": SportEvent(
        name="Running/Sprints",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        loc=SportLocation.tum_courts,
        organizer_names=["Zsofi", "William"],
        icon=":running:",
        min_player_val=3,
    ),
    "Basketball": SportEvent(
        name="Basketball",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        loc=SportLocation.tum_courts,
        organizer_names=["Juan"],
        icon=":basketball:",
        min_player_val=8,
    ),
    # Tuesday events
    "Chess": SportEvent(
        name="Chess",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        loc=SportLocation.mpa_common_room,
        organizer_names=["David"],
        icon=":chess_pawn:",
        min_player_val=3,
    ),
    "Tennis": SportEvent(
        name="Tennis",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        loc=SportLocation.ipp_courts,
        organizer_names=["???"],
        icon=":tennis:",
        min_player_val=4,
    ),
    "Football": SportEvent(
        name="Football",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        loc=SportLocation.ipp_courts,
        organizer_names=["Matteo"],
        icon=":soccer:",
        min_player_val=11,
    ),
    # Thursday events
    "Capture the flag": SportEvent(
        name="Capture the flag",
        start=datetime(2024, 5, 2, 18, 00),
        end=datetime(2024, 5, 2, 19, 00),
        loc=SportLocation.tum_courts,
        organizer_names=["Benny", "Zsofi"],
        icon=":triangular_flag_on_post:",
        min_player_val=8,
    ),
    "Spikeball": SportEvent(
        name="Spikeball",
        start=datetime(2024, 5, 2, 17, 30),
        end=datetime(2024, 5, 2, 21, 00),
        loc=SportLocation.tum_courts,
        organizer_names=["Fabi"],
        icon=":full_moon:",
        min_player_val=4,
    ),
    # Friday events
    "Beer Pong": SportEvent(
        name="Beer Pong",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.mpa_common_room,
        organizer_names=["Benny", "William"],
        icon=":beer:",
        min_player_val=6,
    ),
    "Ping Pong": SportEvent(
        name="Ping Pong",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.mpa_common_room,
        organizer_names=["Fabi", "Zsofi"],
        icon=":ping_pong:",
        min_player_val=4,
    ),
    "Fooseball": SportEvent(
        name="Fooseball",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.mpa_common_room,
        organizer_names=["Matteo"],
        icon=":boom:",
        min_player_val=4,
    ),
}
for event in SPORTS_EVENTS.values():
    fpath = DATAPATH.joinpath(f"sport_descriptions/{event.sanitized_name}.md")
    if not fpath.exists():
        fpath.write_text("NO DESCRIPTION YET\n## Rules\n\n## Format")
