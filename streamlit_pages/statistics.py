import streamlit as st

import helper_functions as hf

_INTRO_TEXT = f"""# Statistics

We're pretty sure you're a nerd like we are, so you might have fun playing around with the data of our {len(hf.DATA_NOW.players)} participants.

We are therefore providing a few tools to visualize the data of our participants.
"""
st.write(_INTRO_TEXT)


with st.expander("Venn Diagram Of Sports Overlaps", expanded=False):
    st.write(
        f"Oh mighty Venn Diagrams, our beloved way to display overlaps... Here you may choose the sports you want to explore."
    )
    selected_keys = hf.st_display_venn_sport_selection(hf.DATA_NOW)
    hf.st_display_overlap_of_sports(selected_keys, hf.DATA_NOW)

with st.expander("Institute Distribution", expanded=False):
    st.write(
        "Here you can see the distribution of participants w.r.t. institutes and career status."
    )
    hf.st_display_institute_dist_plot(hf.DATA_NOW.players)

with st.expander("Sign-Up Times", expanded=False):
    st.write(
        "Oh, don't we all love to procrastinate the simple things such as filling out a 2 minute survey? Well, the following plot seems to support that hypothesis (although we of course don't judge :D)"
    )
    hf.st_display_signup_times(hf.DATA_NOW)

with st.expander("Building the teams", expanded=False):
    st.write("Here we'll soon display how the teams were built.")

with st.expander("Scheduling the matches", expanded=False):
    st.write("Here we'll soon display how we scheduled the matches.")
