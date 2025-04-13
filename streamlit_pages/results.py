import streamlit as st

import helper_functions as hf

_INTRO_TEXT = """# FAQ, results and more

On this page, you can find an overview of the results of the sports week plus some info on the top scorers, an FAQ and a changelog of this website.
"""
st.write(_INTRO_TEXT)

tab_names = [
    "❓FAQ",
    "📊Results",
    "⭐Top Scorers",
    "📜Changelog",
]
tabs = st.tabs(tab_names)
# Results tab:
with tabs[1]:
    # st.write(
    #     "You're probably wondering who's currently in the lead...\\\n All will be revealed at the award ceremony, 21:00 at the MPA seminar room!"
    # )
    # if hf.DATAPATH.joinpath("hidden").exists():
    hf.st_display_full_results(hf.DATA_NOW)
# Scorers tab:
with tabs[2]:
    st.write(
        "The top scorers of each team will be revealed at the end of each week in order for the mystery to build up - just do your best and you might end up in the top 25!"
    )
    # if hf.DATAPATH.joinpath("hidden").exists():
    # hf.st_display_top_scorers(hf.DATA_NOW)
# FAQ tab:
with tabs[0]:
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
