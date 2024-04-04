from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from ..constants import DATAPATH
from ..sport_event_registry import SPORTS_EVENTS


@dataclass
class SportsOrganizer:
    """A person responsible for organizing a sports event."""

    name: str
    """The name of the organizer."""

    email: str
    """The email of the organizer."""

    sport_keys: list[str]
    """The key for the sports that are organized by this person."""

    is_committee_member: bool = False
    """Whether this organizer is also part of the organizing committee."""

    def __post_init__(self):
        for sport_key in self.sport_keys:
            if sport_key not in SPORTS_EVENTS:
                raise ValueError(f"Sport key {sport_key} not found in SPORTS_EVENTS.")

        assert (
            self.email == "" or "@" in self.email and self.email.endswith("...")
        ), f"Provide an obscured email please, not {self.email}."

    @property
    def pic_path(self) -> Path:
        return DATAPATH.joinpath(f"assets/organizer_pics/{self.name.lower()}.png")

    def write_streamlit_rep(self):
        """Write the organizer's information to the Streamlit app."""
        container = st.container(border=True)
        if self.pic_path.exists():
            col1, col2 = container.columns([0.2, 0.8])
            col1.image(str(self.pic_path), use_column_width=True)
        else:
            col2 = container
        committee_str = "\\*" if self.is_committee_member else ""
        text = f"**{self.name}{committee_str}**\\\n"
        email = self.email.replace("@", "<span>@</span>")
        text += f"Email: *{email}*\\\n"
        text += "Sports:\\\n"
        text += ", ".join([SPORTS_EVENTS[sport].html_url for sport in self.sport_keys])
        col2.write(text, unsafe_allow_html=True)
