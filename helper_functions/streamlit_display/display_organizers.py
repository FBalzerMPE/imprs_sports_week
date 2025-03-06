import streamlit as st
from ..data_registry import DataRegistry


def st_display_organizers(data: DataRegistry, add_pic_toggle: bool = False):
    if add_pic_toggle:
        show_pics = (
            st.radio(
                "Hide pictures",
                ["No", "Yes"],
                horizontal=True,
                help="Whether to hide organizer pics (might be better on mobile).",
            )
            == "No"
        )
    else:
        show_pics = True
    col1, col2 = st.columns(2)

    for i, sports_organizer in enumerate(data.organizers.values()):
        if i % 2 == 0:
            with col1:
                sports_organizer.write_streamlit_rep(show_pics)
        else:
            with col2:
                sports_organizer.write_streamlit_rep(show_pics)
