import streamlit as st

import helper_functions as hf

hf.st_set_up_header_and_sidebar()


markdown_text = hf.read_event_desc("../helper_texts/statistics")
st.markdown(markdown_text, unsafe_allow_html=True)
c = hf.create_sport_dist_altair_chart()
st.altair_chart(c, theme="streamlit", use_container_width=True)

markdown_text = hf.read_event_desc("../helper_texts/results")
