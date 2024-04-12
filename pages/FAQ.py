import helper_functions as hf
import streamlit as st

hf.st_set_up_header_and_sidebar()

markdown_text = hf.read_event_desc("../helper_texts/faq")
st.markdown(markdown_text, unsafe_allow_html=True)
