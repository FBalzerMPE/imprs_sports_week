from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import ALL_DAYS, SPORTS_LIST, FpathRegistry
from .match import Match

if TYPE_CHECKING:
    from .sport_event import SportEvent


@dataclass
class Player:
    nickname: str
    """The nickname of this player."""

    avail_days: list[str]
    """The days where this player is available."""

    main_team_letter: str
    """The team this player is part of."""

    subteams: dict[str, str]
    """The subteams this player is part of."""

    matches: list[Match] = field(repr=False)
    """The matches this player is part of."""

    is_late_signup: bool = False
    """Whether this player is a late signup."""

    has_paid_fee: bool = False
    """Whether this player has paid the fee."""

    institute: str = ""
    """The institute this player is from."""

    attended_before: bool = False
    """Whether this player has attended previous sports weeks"""

    confirmation_status: bool = False
    """The confirmation status; has this player replied to the schedule email?"""

    @classmethod
    def from_series(cls, series: pd.Series, all_matches: list[Match]) -> Player:
        name = series["nickname"]
        avail_days = [
            day for day in ALL_DAYS if day in series and series[f"avail_{day}"]
        ]
        team = series["Team"].replace("Team ", "") if "Team" in series else "X"
        if team == "X":
            subteams = {sport: "X" for sport in SPORTS_LIST if series[sport]}
        else:
            subteams = {
                sport: (
                    f"{team}: {subteam}"
                    if sport != "ping_pong" or subteam == "R"
                    else f"{team}: {subteam:0>2}"
                )
                for sport in SPORTS_LIST
                if f"subteam_{sport}" in series
                and (subteam := series.fillna("")[f"subteam_{sport}"]) != ""
            }
        matches = [match_ for match_ in all_matches if match_.contains_player(name)]
        matches = sorted(matches, key=lambda match_: match_.start)
        return cls(
            nickname=name,
            avail_days=avail_days,
            main_team_letter=team,
            subteams=subteams,
            matches=matches,
            is_late_signup=series["late_entry"],
            has_paid_fee=series.get("has_paid_fee", False),
            institute=series["institute"],
            attended_before=series.get("attended_before", False),
            confirmation_status=series["confirmation_status"],
        )

    @property
    def info_str(self) -> str:
        from ..data_registry import DATA_NOW

        is_in_team = self.main_team_letter != "X"

        team_info = f"Team {self.main_team_letter}: " if is_in_team else ""
        text = f"### {team_info}{self.nickname}\n\n"
        if self.attended_before:
            text += "⭐Joins the 2nd time!\\\n"
        else:
            text += "☆First time participant!\\\n"
        sport_str = "participating in" if is_in_team else "signed up for"
        text += f"**Sports {sport_str}:**\\\n"
        text += ", ".join(
            [DATA_NOW.sport_events[sport].html_url for sport in self.subteams]
        )
        if len(self.subteams) == 0:
            text += "Player unfortunately dropped out."
        if is_in_team:
            text += "\\\n"
            confirmation_str = (
                "Confirmed" if self.confirmation_status else "No reply yet"
            )
            text += f"Reply status: **{confirmation_str}**"
        else:
            text += "\\\n"
            money_str = "💸 Has paid" if self.has_paid_fee else ":warning: Not paid yet"
            text += f"Fee status: **{money_str}**"
        return text

    @property
    def sports_days(self) -> dict[str, list[SportEvent]]:
        """The days relevant for this player."""
        from ..data_registry import DATA_NOW

        days = {day: [] for day in ALL_DAYS}
        for match in self.matches:
            if match.sport == "ping_pong" and len(days[match.weekday]) == 0:
                days[match.weekday].append(DATA_NOW.sport_events["ping_pong"])
        for day in ALL_DAYS:
            for event in DATA_NOW.sport_events.values():
                if day not in event.days or event.sanitized_name == "ping_pong":
                    continue
                if event.sanitized_name not in self.subteams:
                    continue
                days[day].append(event)
        return {k: v for k, v in days.items() if len(v) > 0}

    @property
    def website_schedule(self) -> str:
        text = f"### Team {self.main_team_letter}: {self.nickname}\n\n"
        if len(self.subteams) == 0:
            text += "Player unfortunately dropped out."
        for day, sports in self.sports_days.items():
            text += f"#### {day.capitalize()}\n\n"
            for event in sports:
                matches = [
                    match
                    for match in self.matches
                    if match.sport == event.sanitized_name
                ]
                subteam_key = self.subteams[event.sanitized_name]
                if subteam_key.endswith("D"):
                    text += f"{event.html_url}: Dropped out.\n"
                    continue
                text += f"{event.html_url}: Part of subteam **{subteam_key}**.\\\n"
                if subteam_key.endswith("R"):
                    text += "Scheduled as a reserve player. You might be called upon to jump in.\n\n"
                    continue
                if len(event.requirements) > 0:
                    text += f"**Requirements:** {'; '.join(event.requirements)}.\n\n"
                text += "**Matches**:\\\n"
                if event.sanitized_name == "ping_pong":
                    for match_ in [match for match in matches if match.weekday == day]:
                        text += match_.description + ";\\\n"
                    text = text.rstrip(";\\\n")
                else:
                    if len(matches) == 0:
                        continue
                    if len(matches) == 1:
                        text += matches[0].description
                    else:
                        text += (
                            f"{matches[0].description}, and {matches[1].description}"
                        )
                text += "\n\n"
        return text

    def match_times(self) -> list[tuple[datetime, datetime]]:
        return [(match_.start, match_.end) for match_ in self.matches]

    def get_schedule_for_mail(self) -> str:
        from ..data_registry import DATA_NOW

        text = (
            ""
            if not self.is_late_signup
            else "Since you signed up late, you might only be scheduled as reserve some of your preferred events.\n\n"
        )

        for sport, subteam_key in self.subteams.items():
            subteam_key = sport + "_" + subteam_key.replace(": ", "")
            event = DATA_NOW.sport_events[sport]
            subteam = DATA_NOW.subteams[subteam_key]
            if subteam.sub_key == "D":  # No need for dropouts
                continue
            subteam_key_disp = f"**{subteam_key}**"
            matches = [match for match in self.matches if match.sport == sport]
            vals, ind = np.unique(
                [match_.start.strftime("%A") for match_ in matches], return_index=True
            )

            days = vals[np.argsort(ind)]
            if subteam.is_reserve:
                days = event.days
            days = ", ".join([day.capitalize() for day in days])
            text += f"**{event.icon} {event.name} ({days}):**\\\n"
            if len(event.requirements) > 0:
                text += f"**Requirements:** {'; '.join(event.requirements)}.\n\n"
            if subteam.is_reserve:
                text += "You are scheduled to be a reserve player. "
                if sport in ["spikeball", "tennis", "ping_pong", "foosball", "chess"]:
                    text += "This means that you might receive a late call to join if one of your teammates cannot make it."
                else:
                    if event.num_subteams > 1:
                        text += "This means that you may still choose a subteam to support, and may be substituted in during the games."
                    else:
                        text += "This means that you still may join the event and be substituted in during the games."
            else:
                if event.num_players_per_subteam == 1:
                    text += (
                        f"You will be competing on your own in two separate matches:"
                    )
                else:
                    other_players = [
                        player for player in subteam.players if player != self.nickname
                    ]
                    if event.num_players_per_subteam > 2:
                        other_player_str = (
                            ", ".join(other_players[:-1]) + " and " + other_players[-1]
                        )
                    else:
                        other_player_str = other_players[-1]
                    text += f"You are part of subteam {subteam_key_disp}, together with *{other_player_str}*.\\\nYour matches are:"
                text += "\\\n"
                if sport == "running_sprints":
                    text += f"You are scheduled to attend {matches[0].description}.\n"
                else:
                    if len(matches) == 1:
                        text += f"\t{matches[0].description}"
                    else:
                        text += f"\t{matches[0].description}, and\\\n\t{matches[1].description}\n"
            text += "\n\n"
        return text

    def _write_streamlit_info(self, show_avatars=True, show_inst=False):
        """Get the streamlit representation for this player."""
        if not show_avatars and not show_inst:
            st.write(self.info_str, unsafe_allow_html=True)
            return
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            if show_avatars:
                st.image(
                    FpathRegistry.get_animal_pic_path(self.nickname, from_static=False),
                    use_container_width=True,
                )
            if show_inst:
                st.image(
                    FpathRegistry.get_institute_pic_path(self.institute),
                    use_container_width=True,
                )
        with cols[1]:
            st.write(self.info_str, unsafe_allow_html=True)

    def write_streamlit_rep(
        self, info_only=False, schedule_only=False, show_avatars=True, show_inst=False
    ):
        """Get the streamlit representation for this player."""
        container = st.container(border=True)
        if info_only:
            with container:
                self._write_streamlit_info(
                    show_avatars=show_avatars, show_inst=show_inst
                )
            return
        elif schedule_only:
            with container:
                cols = st.columns([0.2, 0.8])

                cols[0].image(
                    FpathRegistry.get_animal_pic_path(self.nickname, from_static=False),
                    use_container_width=True,
                )
                cols[1].write(self.website_schedule, unsafe_allow_html=True)
            return
        tabs = container.tabs(["Info", "Schedule"])
        with tabs[0]:
            self._write_streamlit_info()
        with tabs[1]:
            st.write(self.website_schedule, unsafe_allow_html=True)
