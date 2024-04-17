import helper_functions as hf
import streamlit as st
from helper_functions.classes.player import Player

hf.st_set_up_header_and_sidebar()

st.write(
    """
This site provides an overview on all of the competing main teams.\\
If you know your team and nickname, you can look up the sports you've been assigned to.

**Hint:** You can sort each table by any of the sports if you want to have an overview of the players.\
You can also double-click on the Avatars to see a slightly bigger version of them :)
"""
)

tabs = st.tabs([team.name for team in hf.ALL_TEAMS])
for tab, team in zip(tabs, hf.ALL_TEAMS):
    with tab:
        team.write_streamlit_rep()

        players = team.player_df.sort_values("nickname").fillna("")
        player_names = sorted(players["nickname"].tolist())

        if f"current_index_{team.name}" not in st.session_state:
            st.session_state[f"current_index_{team.name}"] = 0
        # Add a browsing interface for the players
        cols = st.columns(3, gap="large")
        if cols[0].button(
            "Previous",
            disabled=st.session_state[f"current_index_{team.name}"] == 0,
            key=f"previous-{team.name}",
        ):
            st.session_state[f"current_index_{team.name}"] -= 1
        with cols[2]:
            if st.button(
                "Next",
                disabled=st.session_state[f"current_index_{team.name}"]
                == len(players) - 1,
                key=f"next-{team.name}",
            ):
                st.session_state[f"current_index_{team.name}"] += 1
        with cols[1]:
            box_sel = st.selectbox(
                "Select player",
                player_names,
                index=st.session_state[f"current_index_{team.name}"],
                label_visibility="collapsed",
            )
        st.session_state[f"current_index_{team.name}"] = (
            player_names.index(box_sel)
            if box_sel is not None
            else st.session_state[f"current_index_{team.name}"]
        )
        player = Player.from_series(
            players.iloc[st.session_state[f"current_index_{team.name}"]], hf.ALL_MATCHES
        )
        player.write_streamlit_rep()
