import streamlit as st

from ..classes.player import Player
from ..constants import CURRENT_YEAR
from ..data_registry import DataRegistry


def st_display_team_overview(data: DataRegistry):
    """Displays a page with an overview of all teams and their players belonging to the sports week associated with the data."""
    if not data.has_teams:
        text = "🚧" * 30
        text += "\n\nThe teams for this year haven't been determined yet.\\\nCome back a few days before the sports week starts! You can look at the participants on their own page, or, if you want to read stuff about the team creation that will follow, see the explanation on the FAQ page."
        st.write(text)
        st.page_link(
            "streamlit_pages/participants.py",
            label="Head to Participants",
            icon="👨‍👩‍👦",
            use_container_width=True,
        )
        st.page_link(
            "streamlit_pages/Statistics.py",
            label="Head to FAQ",
            icon="📊",
            use_container_width=True,
        )
        return
    tabs = st.tabs([team.name for team in data.teams])
    for tab, team in zip(tabs, data.teams):
        with tab:
            team.write_streamlit_rep()

            if data.year != CURRENT_YEAR:
                continue

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
                players.iloc[st.session_state[f"current_index_{team.name}"]],
                data.matches,
            )
            player.write_streamlit_rep()
