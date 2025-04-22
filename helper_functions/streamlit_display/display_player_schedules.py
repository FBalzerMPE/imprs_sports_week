import pandas as pd
import streamlit as st

from ..classes.match import Match
from ..classes.player import Player


def st_display_player_schedules(
    players: pd.DataFrame, key: str, matches: list[Match], schedule_only: bool = False
):
    players = players.sort_values("nickname").fillna("")
    player_names = sorted(players["nickname"].tolist())

    if f"player_scroll_idx_{key}" not in st.session_state:
        st.session_state[f"player_scroll_idx_{key}"] = 0
    # Add a browsing interface for the players
    cols = st.columns(3, gap="large")
    if cols[0].button(
        "Previous",
        disabled=st.session_state[f"player_scroll_idx_{key}"] == 0,
        key=f"previous-{key}",
    ):
        st.session_state[f"player_scroll_idx_{key}"] -= 1
    with cols[2]:
        if st.button(
            "Next",
            disabled=st.session_state[f"player_scroll_idx_{key}"] == len(players) - 1,
            key=f"next-{key}",
        ):
            st.session_state[f"player_scroll_idx_{key}"] += 1
    with cols[1]:
        box_sel = st.selectbox(
            "Select player",
            player_names,
            index=st.session_state[f"player_scroll_idx_{key}"],
            label_visibility="collapsed",
        )
    st.session_state[f"player_scroll_idx_{key}"] = (
        player_names.index(box_sel)
        if box_sel is not None
        else st.session_state[f"player_scroll_idx_{key}"]
    )
    player = Player.from_series(
        players.iloc[st.session_state[f"player_scroll_idx_{key}"]], matches
    )
    player.write_streamlit_rep(schedule_only=schedule_only)
