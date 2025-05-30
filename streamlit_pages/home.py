from typing import Sequence

import streamlit as st

import helper_functions as hf

# from helper_functions.streamlit_display.display_running_sprints_results import (
#     display_running_sprints_results,
# )

# display_running_sprints_results(hf.DATA_NOW)

st.write(f"# Welcome to the {hf.CURRENT_YEAR} INTER-INSTITUTE SPORTS WEEK in Garching!")

with st.expander(f"This Year's Poster", expanded=False):
    st.image(hf.DATAPATH.joinpath(f"2025/sports_week_poster.png"))

markdown_text = hf.read_event_desc("../helper_texts/introduction")

replace_dict = {
    "SIGNUP_DEADLINE": "**April 4th**",
    "NUM_SIGNUPS": str(len(hf.DATA_NOW.players)),
    "NUM_EVENTS": str(len(hf.DATA_NOW.sport_events)),
    "NUM_MATCHES": str(len(hf.DATA_NOW.matches)),
    "NUM_ORGANIZERS": str(len(hf.DATA_NOW.organizers)),
}
for k, v in replace_dict.items():
    markdown_text = markdown_text.replace(k, v)


def _organizer_filter_func(
    organizers: Sequence[hf.SportsOrganizer],
) -> list[hf.SportsOrganizer]:
    """Filter out the organizers that are no cash contact points."""
    orgs = [org for org in organizers if org.is_cash_contact_point]
    return sorted(orgs, key=lambda x: x.institute)


# parts = markdown_text.split("PAYMENT_POINT_EXPANDER")
# st.write(parts[0], unsafe_allow_html=True)
# with st.expander("Where to pay the 2 € sign-up fee"):
#     st.write(
#         'You can either pay the 2 € via PayPal (see the initial email for address, and make sure we can trace it back to you), or in cash to the designated contact person at your institute (for the proper email domain translation see <a href="contact" target="_self">here</a>):',
#         unsafe_allow_html=True,
#     )
#     hf.st_display_organizers(hf.DATA_NOW, filter_func=_organizer_filter_func)
# markdown_text = parts[1]


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
new_parts = parts[1].split("TEAM_LINKS")
st.write(new_parts[0], unsafe_allow_html=True)
cols = st.columns(2)
cols[0].page_link(
    f"streamlit_pages/participants.py",
    label="Participants",
    icon="👨‍👩‍👦",
    use_container_width=True,
)
cols[1].page_link(
    f"streamlit_pages/Teams.py",
    label="Teams",
    icon="🏅",
    use_container_width=True,
)
st.write(new_parts[1], unsafe_allow_html=True)

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
