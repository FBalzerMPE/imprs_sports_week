from typing import Sequence

import streamlit as st

import helper_functions as hf

st.write(f"# Welcome to the {hf.CURRENT_YEAR} Inter-Institute Sports Week in Garching!")

with st.expander(f"This Year's Poster"):
    st.image(hf.DATAPATH.joinpath(f"2025/sports_week_poster.png"))

markdown_text = hf.read_event_desc("../helper_texts/introduction")
markdown_text = markdown_text.replace("SIGNUP_DEADLINE", "**April 4th**")


def _organizer_filter_func(
    organizers: Sequence[hf.SportsOrganizer],
) -> list[hf.SportsOrganizer]:
    """Filter out the organizers that are no cash contact points."""
    orgs = [org for org in organizers if org.is_cash_contact_point]
    return sorted(orgs, key=lambda x: x.institute)


parts = markdown_text.split("PAYMENT_POINT_EXPANDER")
st.write(parts[0], unsafe_allow_html=True)
with st.expander("Where to pay the 2 € sign-up fee"):
    st.write(
        'You can either pay the 2 € via PayPal (see the initial email for address, and make sure we can trace it back to you), or in cash to the designated contact person at your institute (for the proper email domain translation see <a href="contact" target="_self">here</a>):',
        unsafe_allow_html=True,
    )
    hf.st_display_organizers(hf.DATA_NOW, filter_func=_organizer_filter_func)
markdown_text = parts[1]


for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
    md_key = day.upper() + "_LINKS"
    parts = markdown_text.split(md_key)

    st.write(parts[0], unsafe_allow_html=True)
    markdown_text = parts[1]
    day_sports = [
        event
        for event in hf.DATA_NOW.sport_events.values()
        if day in event.days and event.sanitized_name != "ping_pong"
    ]
    with st.container(border=True):
        cols = st.columns(len(day_sports) + 1)
    cols[0].write(day.capitalize())

    for col, sport in zip(cols[1:], day_sports):
        with col:
            sport.st_display_page_link(True)
parts = markdown_text.split("PING_PONG_LINK")
st.write(parts[0], unsafe_allow_html=True)
hf.DATA_NOW.sport_events["ping_pong"].st_display_page_link(True)
st.write(parts[1], unsafe_allow_html=True)

# # for event in hf.DATA_NOW.sport_events.values():
# #     if day in event.days and event.sanitized_name != "ping_pong":
# #         event.st_get_page_link()
# # relevant_links = [
# #     event.html_url
# #     for event in hf.DATA_NOW.sport_events.values()
# #     if day in event.days and event.sanitized_name != "ping_pong"
# # ]
# # links = ", ".join(relevant_links[:-1]) + " and " + relevant_links[-1]

# # markdown_text = markdown_text.replace(md_key, links)

# st.markdown(markdown_text, unsafe_allow_html=True)
