import streamlit as st

import helper_functions as hf

hf.st_set_up_header_and_sidebar()

_INTRO_TEXT = """On this page, you can see an overview of the results of the sports week, as well as some extra stuff to read about top-scoring players, player numbers and so on.
"""
st.write(_INTRO_TEXT)

tab_names = ["📊Results", "⭐Top Scorers", "📋Team Creation", "❓FAQ"]
tabs = st.tabs(tab_names)
# Results tab:
with tabs[0]:
    # st.write(
    #     "You're probably wondering who's currently in the lead...\\\n All will be revealed at the award ceremony, 21:00 at the MPA seminar room!"
    # )
    # if hf.DATAPATH.joinpath("hidden").exists():
    hf.st_display_full_results()
# Scorers tab:
with tabs[1]:
    # st.write(
    #     "You're probably wondering who's currently in the lead...\\\n All will be revealed at the award ceremony, 21:00 at the MPA seminar room!"
    # )
    # if hf.DATAPATH.joinpath("hidden").exists():
    hf.st_display_top_scorers()
# Team creation tab:
with tabs[2]:
    st.write("### Player distribtions and more")
    c = hf.create_sport_dist_altair_chart()
    st.altair_chart(c, theme="streamlit", use_container_width=True)
    markdown_text = hf.read_event_desc("../helper_texts/statistics")
    st.markdown(markdown_text, unsafe_allow_html=True)
# FAQ tab:
with tabs[3]:
    markdown_text = hf.read_event_desc("../helper_texts/faq")
    questions = markdown_text.split("\n\n")
    header = questions.pop(0)
    for q, a in zip(questions[::2], questions[1::2]):
        with st.expander(q):
            st.write(a, unsafe_allow_html=True)
