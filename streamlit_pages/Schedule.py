from datetime import datetime, time, timedelta

import streamlit as st
from streamlit_calendar import calendar

import helper_functions as hf

st.write(f"# Sports Schedule {hf.CURRENT_YEAR}")

sports_resources = [
    {"id": event.identity_name, "title": event.icon}
    for event in hf.DATA_NOW.sport_events.values()
]
sports_resources.append({"id": "awards", "title": "🏆"})

# The calendar needs an extra day for the date range.
date_range = (hf.DATA_NOW.start_date, hf.DATA_NOW.end_date + timedelta(days=1))

calendar_options = {
    "editable": "false",
    "selectable": "false",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "resourceTimelineDay,resourceTimelineWeek",
    },
    "initialDate": hf.DATA_NOW.start_date.strftime("%Y-%m-%d"),
    "validRange": {
        "start": date_range[0].strftime("%Y-%m-%d"),
        "end": date_range[1].strftime("%Y-%m-%d"),
    },
    "slotMinTime": "17:30:00",
    "slotMaxTime": "21:30:00",
    "initialView": "resourceTimeline",
    "resources": sports_resources,
    "resourceAreaWidth": "10%",
    "resourceLabel": "test",
    "height": "1000px",
}

calendar_events = [
    entry
    for event in hf.DATA_NOW.sport_events.values()
    for entry in event.calendar_entries
]

award_event = {
    "title": "🏆 Award Ceremony (more info will follow)",
    "start": datetime.combine(hf.DATA_NOW.end_date, time(21)).isoformat(),
    "end": datetime.combine(hf.DATA_NOW.end_date, time(21, 30)).isoformat(),
    "resourceId": "awards",
    "color": "green",
}
calendar_events.append(award_event)  # type: ignore

calendar_events += [
    entry
    for event in hf.DATA_NOW.sport_events.values()
    for entry in event.match_calendar_entries
]
if hf.DATA_NOW.has_teams:
    st.write(
        "Go to the individual sports' pages for more detailed information on the schedules (and, if available, also results)."
    )
else:
    st.write(
        "This is the overall schedule, which will be updated soon with the individual match-ups."
    )
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
