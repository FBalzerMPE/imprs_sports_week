import streamlit as st

import helper_functions as hf

hf.st_set_up_header_and_sidebar()

markdown_text = hf.read_event_desc("../helper_texts/introduction")
for day in ["monday", "tuesday", "thursday", "friday"]:
    md_key = day.upper() + "_LINKS"
    relevant_links = [
        event.html_url
        for event in hf.SPORTS_EVENTS.values()
        if day in event.days and event.sanitized_name != "ping_pong"
    ]
    links = ", ".join(relevant_links[:-1]) + " and " + relevant_links[-1]

    markdown_text = markdown_text.replace(md_key, links)
markdown_text = markdown_text.replace(
    "PING_PONG_LINK", hf.SPORTS_EVENTS["ping_pong"].html_url
)
st.markdown(markdown_text, unsafe_allow_html=True)
