from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar

import helper_functions as hf

hf.st_set_up_header_and_sidebar()

sports_resources = [
    {"id": event.identity_name, "title": event.icon}
    for event in hf.SPORTS_EVENTS.values()
]
sports_resources.append({"id": "awards", "title": "🏆"})

calendar_options = {
    "editable": "false",
    "selectable": "false",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "resourceTimelineDay,resourceTimelineWeek",
    },
    "initialDate": "2024-04-29",
    "validRange": {"start": "2024-04-29", "end": "2024-05-04"},
    "slotMinTime": "17:30:00",
    "slotMaxTime": "21:30:00",
    "initialView": "resourceTimeline",
    "resources": sports_resources,
    "resourceAreaWidth": "10%",
    "resourceLabel": "test",
    "height": "1000px",
}

calendar_events = [
    entry for event in hf.SPORTS_EVENTS.values() for entry in event.calendar_entries
]

award_event = {
    "title": "🏆 Award Ceremony (more info will follow)",
    "start": datetime(2024, 5, 3, 21).isoformat(),
    "end": datetime(2024, 5, 3, 21, 30).isoformat(),
    "resourceId": "awards",
    "color": "green",
}
calendar_events.append(award_event)  # type: ignore

calendar_events += [
    entry
    for event in hf.SPORTS_EVENTS.values()
    for entry in event.match_calendar_entries
]
my_calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    # custom_css=custom_css,
    callbacks=["eventClick"],
)
if "eventClick" in my_calendar:
    try:
        url = my_calendar["eventClick"]["event"]["extendedProps"]["url"]
        st.switch_page("pages/events" + url + ".py")
    except KeyError:
        pass
