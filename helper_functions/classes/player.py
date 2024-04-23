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

    confirmation_status: bool = False
    """The confirmation status; has this player replied to the schedule email?"""

    @classmethod
    def from_series(cls, series: pd.Series, all_matches: list[Match]) -> Player:
        name = series["nickname"]
        avail_days = [day for day in ALL_DAYS if series[f"avail_{day}"]]
        team = series["Team"].replace("Team ", "")
        subteams = {
            sport: f"{team}: {subteam}"
            for sport in SPORTS_LIST
            if (subteam := series[f"subteam_{sport}"]) != ""
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
            confirmation_status=series["confirmation_status"],
        )

    @property
    def info_str(self) -> str:
        from ..sport_event_registry import SPORTS_EVENTS

        text = f"### Team {self.main_team_letter}: {self.nickname}\n\n"
        text += "**Sports:**\\\n"
        text += ", ".join([SPORTS_EVENTS[sport].html_url for sport in self.subteams])
        if len(self.subteams) == 0:
            text += "Player unfortunately dropped out."
        text += "\\\n"
        confirmation_str = "Confirmed" if self.confirmation_status else "No reply yet"
        text += f"Reply status: **{confirmation_str}**"
        return text

    @property
    def sports_days(self) -> dict[str, list[SportEvent]]:
        """The days relevant for this player."""
        from ..sport_event_registry import SPORTS_EVENTS

        days = {day: [] for day in ALL_DAYS}
        for match in self.matches:
            if match.sport == "ping_pong" and len(days[match.weekday]) == 0:
                days[match.weekday].append(SPORTS_EVENTS["ping_pong"])
        for day in ALL_DAYS:
            for event in SPORTS_EVENTS.values():
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
                text += f"{event.html_url}: Part of subteam **{subteam_key}**.\\\n"
                if subteam_key.endswith("R"):
                    text += "Scheduled as a reserve player.\n\n"
                    continue
                text += "**Matches**:\\\n"
                if event.sanitized_name == "ping_pong":
                    for match_ in [match for match in matches if match.weekday == day]:
                        text += match_.description + ";\\\n"
                    text = text.rstrip(";\\\n")
                else:
                    text += f"{matches[0].description}, and {matches[1].description}"
                text += "\n\n"
        return text

    def match_times(self) -> list[tuple[datetime, datetime]]:
        return [(match_.start, match_.end) for match_ in self.matches]

    def get_schedule_for_mail(self) -> str:
        from ..data_registry import ALL_SUBTEAMS
        from ..sport_event_registry import SPORTS_EVENTS

        text = (
            ""
            if not self.is_late_signup
            else "Since you signed up late, you are for now only scheduled as reserve for the events you signed up for.\n\n"
        )

        for sport, subteam_key in self.subteams.items():
            event = SPORTS_EVENTS[sport]
            subteam = ALL_SUBTEAMS[sport + "_" + subteam_key]
            subteam_key = f"**{subteam_key}**"
            matches = [match for match in self.matches if match.sport == sport]
            vals, ind = np.unique(
                [match_.start.strftime("%A") for match_ in matches], return_index=True
            )

            days = vals[np.argsort(ind)]
            if subteam.is_reserve:
                days = event.days
            days = ", ".join([day.capitalize() for day in days])
            text += f"**{event.icon} {event.name} ({days}):**\\\n"
            if subteam.is_reserve:
                text += "You are scheduled to be a reserve player. "
                if sport in ["spikeball", "tennis", "table_tennis", "foosball"]:
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
                    text += f"You are part of subteam {subteam_key}, together with *{other_player_str}*.\\\nYour matches are:"
                text += "\\\n"
                if sport == "running_sprints":
                    text += f"You are scheduled to attend {matches[0].description}.\n"
                else:
                    text += f"\t{matches[0].description}, and\\\n\t{matches[1].description}\n"
            text += "\n\n"
        return text

    def write_streamlit_rep(self):
        """Get the streamlit representation for this player."""
        container = st.container(border=True)
        tabs = container.tabs(["Info", "Schedule"])
        with tabs[0]:
            cols = st.columns(2)
            with cols[0]:
                st.image(
                    FpathRegistry.get_animal_pic_path(self.nickname, from_static=False),
                    use_column_width=True,
                )
            with cols[1]:
                st.write(self.info_str, unsafe_allow_html=True)
        with tabs[1]:
            st.write(self.website_schedule, unsafe_allow_html=True)
