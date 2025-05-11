from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import CURRENT_YEAR, DATAPATH, SPORTS_LIST, FpathRegistry
from ..data_registry import DataRegistry, get_data_for_year
from ..logger import LOGGER
from ..streamlit_display import create_map_plot, st_style_df_with_team_vals
from ..util import turn_series_list_to_dataframe
from .match import Match
from .sport_location import SportLocation
from .sports_organizer import SportsOrganizer
from .subteam import Subteam


def display_ping_pong_loc_descs():
    tabs = st.tabs(["MPE Table", "IPP Table 1", "IPP Table 2"])
    impath = str(DATAPATH.joinpath("assets/location_pics")) + "/"
    with tabs[0]:
        st.write(
            "Enter the MPE building, e.g. through the main entrance.\\\nAfter entering, turn right and follow the corridor to the end in front of the staircase."
        )
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t1_1.jpg", width=300)
        with cols[1]:
            st.image(impath + "t1_2.jpg", width=300)
        st.write("There, turn left and then right immediately.")
        st.image(impath + "t1_3.jpg", width=300)
        st.write("Walk about 10 m before turning left and walk by the big scales.")
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t1_4.jpg", width=300)
        with cols[1]:
            st.image(impath + "t1_5.jpg", width=300)
        st.write(
            "Now just follow the corridor up to the end until you arrive at the door with the staircase leading to the room with the table."
        )
        st.image(impath + "t1_6.jpg", width=300)
    with tabs[1]:
        st.write("The following picture shows where you're coming from.")
        st.image(impath + "t2_1.jpg", width=300)
        st.write("Walk past the building and turn right to enter the door.")
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t2_2.jpg", width=300)
        with cols[1]:
            st.image(impath + "t2_3.jpg", width=300)
        st.write(
            "There, walk through until the end, turn left and you should see the staircase on the right to go up. On the first floor, you should already see the door with the sign for table tennis. It shouldn't be locked; in the case it is, give Fabi or Zsofi a call."
        )
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t2_4.jpg", width=300)
        with cols[1]:
            st.image(impath + "t2_5.jpg", width=300)
        st.write("You made it! Have a good match!.")
        st.image(impath + "t2_6.jpg", width=300)
    with tabs[2]:
        st.write(
            "If you're coming from Garching Forschungszentrum/the IPP main gate and walk straight, you should see the following sign on the right. There, turn right and enter the building."
        )
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t3_1.jpg", width=300)
        with cols[1]:
            st.image(impath + "t3_2.jpg", width=300)
        st.write("Right after entering, follow the staircase downwards, and turn left.")
        cols = st.columns(2)
        with cols[0]:
            st.image(impath + "t3_3.jpg", width=300)
        with cols[1]:
            st.image(impath + "t3_4.jpg", width=300)
        st.write("You made it! Have a good match!.")
        st.image(impath + "t3_5.jpg", width=300)


def _st_display_match_df(
    df: pd.DataFrame,
    only_one_player_per_team: bool,
    pitch_name: str,
    data: DataRegistry,
):
    """Style the match dataframe and display it properly."""
    df = df.infer_objects(copy=False).fillna("")  # type: ignore
    df = df.sort_values(["time", "location"])
    for col in ["location", "day"]:
        if len(np.unique(df[col])) == 1:
            df = df.drop(columns=col)
    name = "Player" if only_one_player_per_team else "Team"
    p_display_width = None if only_one_player_per_team else "small"
    column_configs = {}
    column_configs["time"] = st.column_config.Column("Time")
    column_configs["location"] = st.column_config.Column(pitch_name)
    column_configs["team_a"] = st.column_config.TextColumn(
        f"{name} a", width=p_display_width
    )
    column_configs["team_b"] = st.column_config.TextColumn(
        f"{name} b", width=p_display_width
    )
    if only_one_player_per_team:
        df["team_a_av"] = df["team_a"].apply(
            lambda x: FpathRegistry.get_animal_pic_path(x[3:])
        )
        df["team_b_av"] = df["team_b"].apply(
            lambda x: FpathRegistry.get_animal_pic_path(x[3:])
        )
        column_configs["team_a_av"] = st.column_config.ImageColumn("Avatar a")
        column_configs["team_b_av"] = st.column_config.ImageColumn("Avatar b")
    column_configs["result"] = st.column_config.Column("Result", width="small")
    column_configs["winner"] = st.column_config.Column("Winner", width="small")
    style = st_style_df_with_team_vals(df, data)
    st.dataframe(
        style,
        hide_index=True,
        column_config=column_configs,
        column_order=[
            "day",
            "time",
            "location",
            "team_a_av",
            "team_a",
            "team_b",
            "team_b_av",
            "result",
            "winner",
        ],
    )


def _st_display_subteam_df(df: pd.DataFrame, data: DataRegistry):
    if len(df) == 0:
        return
    df = df.sort_values(["is_reserve", "full_key"], ascending=[True, True])
    column_configs = {"full_key": st.column_config.Column("Subteam", width="small")}
    for i in range(max(df["players"].apply(len))):
        df[f"avatar_{i}"] = df["players"].apply(
            lambda x: FpathRegistry.get_animal_pic_path(x[i]) if i < len(x) else ""
        )
        column_configs[f"avatar_{i}"] = st.column_config.ImageColumn("")
    column_configs["players"] = st.column_config.ListColumn("Players")
    st.dataframe(
        st_style_df_with_team_vals(df, data, full_row=True),
        hide_index=True,
        column_config=column_configs,
        column_order=[*column_configs],
    )


@dataclass
class RunningEvent:
    name: str
    start: datetime
    end: datetime

    @property
    def as_series(self) -> pd.Series:
        return pd.Series(
            {
                "Name": self.name,
                "Start": self.start.strftime("%H:%M"),
            }
        )

    @property
    def description(self) -> str:
        return f"{self.start.strftime("%H:%M")}: **{self.name}**"

    def get_calendar_entry(self, sport_id: str) -> dict[str, str]:
        return {
            "title": self.name,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "resourceId": sport_id,
            "color": "#006400",
            "borderColor": "black",
        }


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

    pitch_type_name: str
    """How a pitch is called for this sport (important for displaying location)"""

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

    point_weight_factor: float = 1.0
    """The amount by which points achieved for this sport are weighted.
    This roughly depends on the number of players that are actually playing for this sport."""

    year: int = CURRENT_YEAR
    """The year this event is taking place in
    (needed for associated match and subteam loading)."""

    conflicting_sports: list[str] = field(default_factory=list)
    """Any other sports overlapping with this one."""

    requirements: list[str] = field(default_factory=list)
    """Any tools that are neccessary to participate."""

    subteams: list[Subteam] = field(default_factory=list, repr=False)
    """The sub-teams for this sport."""

    matches: list[Match] = field(default_factory=list, repr=False)
    """All matches scheduled for this sport."""

    days: list[str] = field(init=False)
    """The days this sport takes place on."""

    def __post_init__(self):
        assert self.start < self.end, "The start time must be before the end time."
        assert (self.sanitized_name == "running_sprints") or (
            self.num_matches_per_subteam
            * self.num_subteams
            / self.num_pitches
            * self.match_duration
            <= self.end - self.start
        ), f"The {self.name} event is too short for the number of matches and sub-teams."
        self.days = [
            day.strftime("%A").lower()
            for day in pd.date_range(self.start, self.end).date
            # if day.strftime("%A").lower() != "wednesday"
        ]
        self.subteams = [
            subteam
            for subteam in get_data_for_year(self.year).subteams.values()
            if subteam.sport == self.sanitized_name
        ]
        matches = [
            m
            for m in get_data_for_year(self.year).matches
            if m.sport == self.sanitized_name
        ]
        self.matches = sorted(matches, key=lambda m: m.start)

    @classmethod
    def from_dict(
        cls,
        sport_dict: dict,
        locs: dict[str, SportLocation],
        organizers: dict[str, SportsOrganizer],
    ) -> "SportEvent":
        """Create a sport event from a dictionary, e.g. like the ones available in the yearly yaml data."""
        d = sport_dict.copy()
        d["start"] = datetime.fromisoformat(sport_dict["start"])
        d["end"] = datetime.fromisoformat(sport_dict["end"])
        d["match_duration"] = timedelta(minutes=d["match_duration"])
        d["name"] = (
            sport_dict["name"]
            .replace("_", " ")
            .title()
            .replace("Sprints", "and Sprints")
        )
        d["loc"] = locs[sport_dict["loc"]]
        d["organizer_names"] = [
            org.name
            for org in organizers.values()
            if sport_dict["name"] in org.sport_keys
        ]
        return cls(**d, year=d["start"].year)

    @property
    def sanitized_name(self) -> str:
        return self.name.replace(" and ", "_").replace(" ", "_").lower()

    @property
    def identity_name(self) -> str:
        """The identity name, which is basically the index used for
        sorting the sports by appearance."""
        return f"{SPORTS_LIST.index(self.sanitized_name):0>2}"

    @property
    def calendar_entries(self) -> list[dict[str, str | dict]]:
        """The calendar entries with the general timeline for this sport."""
        title = f"{self.icon} {self.name} (Contact: {', '.join(self.organizer_names)})"
        # Put a 15 minute buffer before each event to make people arrive in time
        buf_delta = 0 if self.sanitized_name == "ping_pong" else 15
        buffered_start_time = (self.start - timedelta(minutes=buf_delta)).isoformat()
        base_dict = {
            "title": title,
            "start": buffered_start_time,
            "end": self.end.isoformat(),  # "2024-04-29T21:00:00",
            "resourceId": self.identity_name,
            "extendedProps": {"url": "/" + self.sanitized_name},
        }
        if self.sanitized_name != "ping_pong":
            return [base_dict]
        entries = []
        for day in [(5, 5), (5, 6), (5, 7), (5, 8), (5, 9)]:
            start = datetime(2025, day[0], day[1], 17, 30)
            end = datetime(2025, day[0], day[1], 21, 00)
            new_entry = base_dict.copy()
            new_entry["start"] = start.isoformat()
            new_entry["end"] = end.isoformat()
            entries.append(new_entry)
        return entries

    @property
    def match_calendar_entries(self) -> list[dict[str, str]]:
        """Get the calendar entries for the matches."""
        if self.sanitized_name == "running_sprints":
            from ..sport_event_registry import RUNNING_EVENTS

            return [
                event.get_calendar_entry(self.identity_name) for event in RUNNING_EVENTS
            ]
        return [
            match_.get_calendar_entry(self.identity_name) for match_ in self.matches
        ]

    @property
    def html_url(self) -> str:
        """The way this sport can be reached while staying on the same webpage.
        It's a little clunky but seems to be the only way that works with streamlit.
        Also set to not wrap so icon and name aren't separated."""
        return f'<span style="white-space:nowrap;">{self.icon} <a href="/{self.name}" target="_self">{self.name}</a></span>'

    @property
    def short_info_text(self) -> str:
        contact_link = (
            f'<a href="/contact" target="_self">{", ".join(self.organizer_names)}</a>'
        )
        stats_link = f'<a href="/statistics" target="_self">Results and more</a>'
        loc_name = (
            "Garching Gym; or TUM running fields"
            if self.sanitized_name == "badminton"
            else (
                self.loc.display_name
                if self.sanitized_name != "ping_pong"
                else "Various tables"
            )
        )
        days = (
            "Between 15:45 and 17:45; or between 17:45 and 20:00"
            if self.sanitized_name == "badminton"
            else (
                self.start.strftime("%A, %B %d")
                if self.sanitized_name != "ping_pong"
                else "All week"
            )
        )
        text = f"""
- **Location:** {loc_name} (see also location tab)
- **Time:** {self.start.strftime('%H:%M')} to {self.end.strftime('%H:%M')} on **{days}**
- **Organizers:** {contact_link} (see also contact tab)
- **Point weight factor:** {self.point_weight_factor:.1f} (due to {self.num_players_per_subteam*self.num_subteams*3} attending players)"""
        return text

    @property
    def sub_team_df(self) -> pd.DataFrame:
        return turn_series_list_to_dataframe([team.as_series for team in self.subteams])

    @property
    def match_df(self) -> pd.DataFrame:
        return turn_series_list_to_dataframe([m.as_series for m in self.matches])

    @property
    def single_match_win_value(self) -> float:
        """How much winning a single match contributes to the final score of your team for the individual person."""
        return (
            100
            / self.num_players_per_subteam
            / len(self.matches)
            * self.point_weight_factor
        )

    def st_display_page_link(self, use_container_width=False):
        """Write a streamlit pageLink instance."""
        disabled = self.year != CURRENT_YEAR
        st.page_link(
            f"streamlit_pages/events/{self.sanitized_name}.py",
            label=self.name,
            icon=self.icon,
            use_container_width=use_container_width,
            disabled=disabled,
        )

    def get_clear_name_schedule(self) -> str:
        text = f"## {self.name}\n\n### Subteams\n\n"
        sep = "\n\n" if self.sanitized_name != "ping_pong" else ";\\\n"
        text += sep.join(
            [
                f"**{subteam.full_key}**: "
                + ", ".join(subteam.real_names)
                + "\\\n*"
                + ", ".join(subteam.players)
                + "*"
                for subteam in (sorted(self.subteams, key=lambda s: s.full_key))
            ]
        )
        text += "\n\n### Matches\n\n"
        if self.sanitized_name == "ping_pong":
            for loc in "123":
                text += f"#### Location {loc}\n\n"
                text += "\n\n".join(
                    [m.description for m in self.matches if m.location == loc]
                )
                text += "\n\n"
        elif self.sanitized_name != "running_sprints":
            text += "\n\n".join([m.description for m in self.matches])
        else:
            from ..sport_event_registry import RUNNING_EVENTS

            text += "\n\n".join([event.description for event in RUNNING_EVENTS])
        return text

    def get_attending_players(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.sanitized_name]]

    def _st_display_matches(self):

        if self.sanitized_name in ["basketball", "volleyball"]:
            st.write(
                "⚠️Due to the rain, the Monday matches have been cancelled. Instead, there were free-to-join matches on Friday, starting at 17:30. If you want to join, just stop by! You won't need to be part of any subteam."
            )
        if self.sanitized_name == "running_sprints":
            fpath = FpathRegistry.get_path_running_sprints(self.year)
            if not fpath.exists():
                st.write("No matches have been scheduled yet.")
                return
            from ..data_registry import DATA_NOW
            from ..streamlit_display.display_running_sprints_results import (
                display_running_sprints_results,
            )

            display_running_sprints_results(DATA_NOW)
            st.write(fpath.read_text(encoding="utf-8"))
            # from ..sport_event_registry import RUNNING_EVENTS

            # df = pd.DataFrame([event.as_series for event in RUNNING_EVENTS])
            # st.dataframe(df, hide_index=True)
            return
        if len(self.matches) == 0:
            # LOGGER.warning(f"No matches found for {self.sanitized_name}")
            st.write("No matches have been scheduled yet.")
            return
        is_single = self.num_players_per_subteam == 1
        df = self.match_df
        if self.sanitized_name != "ping_pong":
            if self.sanitized_name == "volleyball":
                df["location"] = df["location"].apply(
                    {"1": "Grass 1", "2": "Grass 2", "3": "Grass 3", "4": "Grass 2"}.get
                )
            if self.sanitized_name == "badminton":
                df["location"] = df["location"].apply(
                    {
                        "1": "Indoor 1",
                        "2": "Indoor 2",
                        "3": "Indoor 3",
                        "4": "Outdoor 1",
                        "5": "Outdoor 2",
                        "6": "Outdoor 3",
                    }.get
                )
            _st_display_match_df(
                df, is_single, self.pitch_type_name, get_data_for_year(self.year)
            )
            return
        # Since ping pong is during the whole week, we display them in a tabbed view
        df["location"] = df["location"].apply(
            {"1": "MPE table", "2": "IPP table 1", "3": "IPP table 2"}.get
        )
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        tabs = st.tabs(days)
        for tab, day in zip(tabs, days):
            with tab:
                sub_df = df[df["day"] == day]
                _st_display_match_df(
                    sub_df, True, self.pitch_type_name, get_data_for_year(self.year)
                )

    def _st_display_subteams(self):
        df = self.sub_team_df
        if len(df) == 0:
            st.write(f"### Subteams\n\nNo subteams have been determined yet.")
            return
        reserve_mask = df["is_reserve"].astype(bool)
        dropout_mask = df["sub_key"] == "D"
        if self.num_players_per_subteam == 1:
            st.write(f"### Reserve players\n")
            if np.sum(reserve_mask) > 0:
                st.write(
                    "The following are the reserve players that may jump in if players cannot make it."
                )
                _st_display_subteam_df(df[reserve_mask], get_data_for_year(self.year))
            else:
                st.write(
                    "There's currently noone that signed up as a reserve player here."
                )
        else:
            st.write(f"### Subteams\n")
            if self.year == 2025 and self.sanitized_name in [
                "basketball",
                "volleyball",
            ]:
                st.write(
                    "The subteams were not set in beforehand for this event as it was a spontaneous replacement - anyone was allowed to join any of the matches for their main team.\n\nSince it was pretty chaotic, we cannot guarantee that the subteams are correct. Let us know if you were forgotten. Also, the subteams changed slightly in between matches, and players jumped in pretty flexibly to help out (which is not properly reflected here).\n\nThe people that joined any subteams were the following:"
                )
                _st_display_subteam_df(
                    df[~reserve_mask & ~dropout_mask], get_data_for_year(self.year)
                )
                st.write(
                    "#### Other players\nThe following players also initially signed up:"
                )
            else:
                st.write("The subteams above consist of the following players:")
                _st_display_subteam_df(
                    df[~reserve_mask & ~dropout_mask], get_data_for_year(self.year)
                )
                st.write(
                    "#### Reserve players\nThe following players may join as substitute players:"
                )
            _st_display_subteam_df(df[reserve_mask], get_data_for_year(self.year))

    def _get_desc_text(
        self, specifier: Literal["introduction", "rules", "specifications"]
    ) -> str:
        subteam_suffix = "subteam" + ("" if self.num_subteams == 1 else "s")
        if self.num_players_per_subteam == 1:
            subteam_suffix = "players"
        rep_dict = {
            "WEIGHT_FACTOR": f"**{self.point_weight_factor}**",
            "ORGANIZERS": " and ".join(self.organizer_names),
            "NUM_PLAYERS_SUBTEAM": f"**{self.num_players_per_subteam}**",
            "NUM_SUBTEAMS": f"**{self.num_subteams} {subteam_suffix}**",
            "LOCATION": self.loc.display_name,
        }
        text = FpathRegistry.get_sport_info_path(
            self.sanitized_name, specifier
        ).read_text(encoding="utf-8")
        for key, val in rep_dict.items():
            text = text.replace(key, val)
        return text

    def write_streamlit_rep(self):
        st.write(f"# {self.name}")
        st.write(self.short_info_text, unsafe_allow_html=True)
        cols = st.columns([0.7, 0.3])
        cols[0].write(self._get_desc_text("introduction"))
        cols[1].image(FpathRegistry.get_sport_pic_path(self.sanitized_name))
        loc_tab_name = (
            "Location"
            if self.sanitized_name not in ["ping_pong", "badminton"]
            else "Locations"
        )
        tab_names = ["Format", "Rules", "Schedule and teams", loc_tab_name, "Contact"]
        tabs = st.tabs(tab_names)
        with tabs[0]:
            st.write(self._get_desc_text("specifications"))
        with tabs[1]:
            st.write(self._get_desc_text("rules"))
        with tabs[2]:
            extra_str = (
                "" if self.num_players_per_subteam == 1 else "subteam compositions and "
            )
            st.write(f"Scroll down to see the {extra_str}reserve players.")
            st.write(f"### Schedule\n")
            self._st_display_matches()

            self._st_display_subteams()
        with tabs[3]:
            locs = [self.loc.key]
            if self.sanitized_name == "ping_pong":
                st.info(
                    f"The matches will take place at various tables scattered around the campus, their locations are marked in red. Hover over them for details.\n\n⚠️Scroll down for more detailed descriptions on how to get to each table!"
                )
                from ..data_registry import ALL_LOCATIONS

                locs = [
                    loc.key for key, loc in ALL_LOCATIONS.items() if "ping_pong" in key
                ]
            if self.sanitized_name == "volleyball":
                st.info(
                    f"The grass courts are going to be set up on the TUM big field.⚠️⚠️⚠️We are NOT playing at the Beach courts as we cannot rely on their availability!"
                )
                # locs.append("tum_big_field")
            else:
                "The location for this event is marked in red, hover over its name to find more information."
            if self.sanitized_name in ["foosball", "beer_pong"]:
                st.write(
                    "In case you have trouble finding the MPA locations, try to enter through the MPA entrance. The MPE entrance will be locked from 17:00 onwards. You can go below it to pass through to MPA, and there go to the basement - you should bump into people there.\\\nIn case you're completely stuck, let us know in the signal group."
                )
            is_badminton = self.sanitized_name == "badminton"
            if is_badminton:
                st.info(
                    f"The outdoor courts are going to be set up on the TUM big field."
                )
                locs.append("tum_big_field")
            create_map_plot(locs, start_zoomed_out=is_badminton)
            if self.sanitized_name == "ping_pong":
                display_ping_pong_loc_descs()
        with tabs[4]:
            text = r"""
Here you can find the contact information for the organizers of this event - don't be shy to write them an email or signal message if you have any questions or need help!\
For spam prevention, the email addresses do not contain the domain beyond the "@" symbol.
The correct address endings are as follows:

- @1... $\rightarrow$ mpe.mpg.de
- @2... $\rightarrow$ mpa-garching.mpg.de
- @3... $\rightarrow$ ipp.mpg.de
- @4... $\rightarrow$ mpp.mpg.de
"""
            st.write(text)
            col1, col2 = st.columns(2)

            for i, name in enumerate(self.organizer_names):
                organizer = get_data_for_year(self.year).organizers[name]
                if i % 2 == 0:
                    with col1:
                        organizer.st_display_info()
                else:
                    with col2:
                        organizer.st_display_info()
