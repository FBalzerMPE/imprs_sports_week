import streamlit as st

import helper_functions as hf

_INTRO_TEXT = """# FAQ, results and more

On this page, you can find an overview of the results of the sports week plus some info on the top scorers, an FAQ and a changelog of this website.
"""
st.write(_INTRO_TEXT)

tab_names = [
    "📊Results",
    "⭐Top Scorers",
    "❓FAQ",
    "📜Changelog",
]
tabs = st.tabs(tab_names)
# Results tab:
with tabs[0]:
    st.write(
        "You're probably wondering who's currently in the lead, but to keep the suspense, we've decided to hide the results for now...\\\nLast time we looked, Team C was slightly ahead, but then Team A and B had strong performances in Spikeball, and there were still Chess, CtF, Basketball, Volleyball, Foosball, Beer Pong and many Ping Pong matches to be played...\\\nAll will be revealed at the award ceremony on Friday 21:45 at the MPA seminar room!"
    )
    if hf.DATAPATH.joinpath("hidden").exists():
        hf.st_display_full_results(hf.DATA_NOW)
# Scorers tab:
with tabs[1]:
    st.write(
        "The top scorers of each team will be revealed at the end of each week in order for the mystery to build up - just do your best and you might end up in the top 25!\n\nHow does it work? For every match you win (even in a team), you are awarded approximately 5 points, and your points are summed up across all sports."
    )
    if hf.DATAPATH.joinpath("hidden").exists():
        hf.st_display_top_scorers(hf.DATA_NOW)
# FAQ tab:
with tabs[2]:
    markdown_text = hf.read_event_desc("../helper_texts/faq")
    questions = markdown_text.split("\n\n")
    header = questions.pop(0)
    for q, a in zip(questions[::2], questions[1::2]):
        with st.expander(q):
            st.write(a, unsafe_allow_html=True)
# Changelog tab:
with tabs[3]:
    st.write(
        "Brief changelog for this website in case you care about that kinda stuff. Might be a bit technical/boring."
    )
    log = hf.get_changelog_data()
    for version, changes in log.items():
        with st.expander(f"Version {version}", expanded=True):
            st.write("- " + "\n- ".join(changes))
