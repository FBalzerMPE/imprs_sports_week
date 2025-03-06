from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from ..constants import CURRENT_YEAR, DATAPATH, SPORTS_LIST, FpathRegistry


def _st_display_text_without_spacing(text: str, spacing_px: int = 5):
    """Display markdown without the extra spacing."""
    t = f"<div style='margin-bottom: {spacing_px}px;'>{text}</div>"
    st.markdown(t, unsafe_allow_html=True)


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

    is_cash_contact_point: bool = False
    """Whether this organizer is a person that can be contacted to deposit the
    entry fee at."""

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
    def is_current_year(self) -> bool:
        return self.year == CURRENT_YEAR

    @property
    def nick_pic_path(self) -> Path:
        return Path(FpathRegistry.get_animal_pic_path(self.nickname, False))

    @property
    def title(self) -> str:
        """The title of the organizer."""
        committee_str = "*" if self.is_committee_member else ""
        inst_str = f" ({self.institute})" if self.institute else ""
        cash_str = "💸" if self.is_cash_contact_point and self.is_current_year else ""
        text = f"{self.name}{committee_str}{inst_str}{cash_str}"
        return text

    def get_desc_text(self, add_cash_str=True) -> str:
        """The description text of the organizer."""
        text = ""
        if add_cash_str and self.is_cash_contact_point and self.is_current_year:
            cash_str = "<br>Contact to pay 2 € sign-up fee"
            text += cash_str
        if self.is_current_year:
            email = self.email.replace("@", "<span>@</span>")
            text += f"<br>Email: <i>{email}</i>"
        return text.lstrip("<br>")

    def _st_display_pics(self):
        """Display the organizer's pictures if available."""
        if self.pic_path.exists():
            st.image(str(self.pic_path), use_container_width=True)
        if self.nick_pic_path.exists():
            st.image(str(self.nick_pic_path), use_container_width=True)

    def _st_display_sports(self):
        """Display the sports by this organizer as link buttons."""
        from ..data_registry import get_data_for_year

        events = get_data_for_year(self.year).sport_events
        if len(self.sport_keys) == 0:
            if self.is_cash_contact_point:
                text = "Cash contact person."
            else:
                text = "No sports organized this year."
            _st_display_text_without_spacing(text)
            return
        sports = [events[sport] for sport in self.sport_keys]
        if self.is_current_year:
            _st_display_text_without_spacing("Contact for:")
        for sport in sports:
            sport.st_display_page_link(True)

    def st_display_info(self, show_pics: bool = True, use_expander: bool = False):
        """Write the organizer's information to the Streamlit app."""

        container = (
            st.expander(self.title) if use_expander else st.container(border=True)
        )
        col_list = [0.8]
        if show_pics and (self.nick_pic_path.exists() or self.pic_path.exists()):
            col_list.insert(0, 0.2)
            cols = container.columns(col_list)
            col = cols[1]
            with cols[0]:
                self._st_display_pics()
        else:
            col = container

        with col:
            if not use_expander:
                title = f"<h5>{self.title}</h5>"
                _st_display_text_without_spacing(title)
            _st_display_text_without_spacing(
                self.get_desc_text(add_cash_str=use_expander)
            )
            self._st_display_sports()
