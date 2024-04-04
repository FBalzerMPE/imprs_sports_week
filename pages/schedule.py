import helper_functions as hf
import streamlit as st
from streamlit_calendar import calendar

hf.st_set_up_header_and_sidebar()

sports_resources = [
    {"id": event.name, "title": event.name, "loc": str(event.loc.titledName)}
    for event in hf.SPORTS_EVENTS.values()
]

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
    "slotMaxTime": "21:00:00",
    "initialView": "resourceTimelineDay",
    "resourceGroupField": "loc",
    "resources": sports_resources,
}
calendar_events = [event.calendar_entry for event in hf.SPORTS_EVENTS.values()]
calendar_events += [
    entry
    for event in hf.SPORTS_EVENTS.values()
    for entry in event.match_calendar_entries
]
custom_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

my_calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    callbacks=["eventClick"],
)
if "eventClick" in my_calendar:
    try:
        url = my_calendar["eventClick"]["event"]["extendedProps"]["url"]
        st.switch_page("pages/events" + url + ".py")
    except KeyError:
        pass
