import helper_functions as hf
import streamlit as st

hf.st_set_up_header_and_sidebar()

markdown_text = hf.read_event_desc("../helper_texts/introduction")
for day in ["monday", "tuesday", "thursday", "friday"]:
    md_key = day.upper() + "_LINKS"
    relevant_links = [
        event.html_url for event in hf.SPORTS_EVENTS.values() if day in event.days
    ]
    links = ", ".join(relevant_links[:-1]) + " and " + relevant_links[-1]

    markdown_text = markdown_text.replace(md_key, links)
st.markdown(markdown_text, unsafe_allow_html=True)
