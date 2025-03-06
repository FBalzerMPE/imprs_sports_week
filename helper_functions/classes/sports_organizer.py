from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from ..constants import CURRENT_YEAR, DATAPATH, SPORTS_LIST, FpathRegistry


@dataclass
class SportsOrganizer:
    """A person responsible for organizing a sports event."""

    name: str
    """The name of the organizer."""

    nickname: str
    """The animal name of the organizer."""

    email: str
    """The email of the organizer."""

    sport_keys: list[str]
    """The key for the sports that are organized by this person."""

    is_committee_member: bool = False
    """Whether this organizer is also part of the organizing committee."""

    institute: str = ""
    """The institute of the organizer."""

    year: int = CURRENT_YEAR
    """The year of the sports week this organizer helped out."""

    def __post_init__(self):
        for sport_key in self.sport_keys:
            if sport_key not in SPORTS_LIST:
                raise ValueError(f"Sport key {sport_key} not found in SPORTS_EVENTS.")
        self.sport_keys = sorted(self.sport_keys)

        assert (
            self.email == "" or "@" in self.email and self.email.endswith("...")
        ), f"Provide an obscured email please, not {self.email}."

    @property
    def pic_path(self) -> Path:
        sani_name = self.name.lower().replace(" ", "_").replace("é", "e")
        return DATAPATH.joinpath(f"assets/organizer_pics/{sani_name}.png")

    @property
    def nick_pic_path(self) -> Path:
        return Path(FpathRegistry.get_animal_pic_path(self.nickname, False))

    def write_streamlit_rep(self, show_pics: bool = True):
        """Write the organizer's information to the Streamlit app."""
        from ..data_registry import get_data_for_year

        events = get_data_for_year(self.year).sport_events
        sports = [events[sport] for sport in self.sport_keys]
        container = st.container(border=True)
        col_list = [0.8]
        if show_pics and (self.nick_pic_path.exists() or self.pic_path.exists()):
            col_list.insert(0, 0.2)
            cols = container.columns(col_list)
            col = cols[1]
        else:
            col = container
        if show_pics and self.pic_path.exists():
            cols[0].image(str(self.pic_path), use_container_width=True)
        if show_pics and self.nick_pic_path.exists():
            cols[0].image(str(self.nick_pic_path), use_container_width=True)

        committee_str = "\\*" if self.is_committee_member else ""
        inst_str = f" ({self.institute})" if self.institute else ""
        text = f"**{self.name}{committee_str}{inst_str}**"
        if self.year == CURRENT_YEAR:
            email = self.email.replace("@", "<span>@</span>")
            text += f"\\\nEmail: *{email}*\\\n"
        if len(self.sport_keys) == 0:
            text += "\\\nNo sports organized this year."
        else:
            if self.year == CURRENT_YEAR:
                text += "\\\nContact for: "
        col.write(text, unsafe_allow_html=True)
        for sport in sports:
            with col:
                sport.st_display_page_link(True)
