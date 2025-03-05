"""Contains all of the events that we are planning to organize."""

from datetime import datetime, timedelta

from .classes.sport_event import RunningEvent

RUNNING_EVENTS = [
    RunningEvent(
        "Warm up", datetime(2025, 4, 29, 17, 30), datetime(2025, 4, 29, 17, 45)
    ),
    RunningEvent(
        "Sprints", datetime(2025, 4, 29, 17, 45), datetime(2025, 4, 29, 18, 5)
    ),
    RunningEvent("Relay", datetime(2025, 4, 29, 18, 5), datetime(2025, 4, 29, 18, 20)),
    RunningEvent(
        "Reaction Games", datetime(2025, 4, 29, 18, 20), datetime(2025, 4, 29, 18, 45)
    ),
    RunningEvent(
        "10-minute run", datetime(2025, 4, 29, 18, 45), datetime(2025, 4, 29, 19, 0)
    ),
]
