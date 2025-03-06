import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

import helper_functions as hf

st.write(
    f"""
# Previous Sports Weeks

Here you can find the results of the previous sports week in 2024, which was a blast!

All in all, an astonishing amount of {len(hf.DATA_2024.players)} players were split into {len(hf.DATA_2024.teams)} main teams and competed in {len(hf.DATA_2024.sport_events)} different sports.
"""
)
st.page_link(
    "streamlit_pages/Statistics.py",
    label="Click here for further info on the current sports week",
    icon="📊",
    use_container_width=True,
)

with st.expander("Poster"):
    pdf_viewer(hf.DATAPATH.joinpath(f"2024/sports_week_poster.pdf"))

with st.expander("Player/Sports Overview"):
    hf.st_display_player_overview(hf.DATA_2024)

with st.expander("Teams"):
    hf.st_display_team_overview(hf.DATA_2024)

with st.expander("Results"):
    hf.st_display_full_results(hf.DATA_2024)

with st.expander("Top Scorers"):
    hf.st_display_top_scorers(hf.DATA_2024)

with st.expander("Organizers"):
    st.write(
        f"The following people helped organize the {hf.DATA_2024.year} sports week. All members of the organizing committee are marked with a \\*."
    )
    hf.st_display_organizers(hf.DATA_2024, False)
