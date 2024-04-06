"""Contains all of the events that we are planning to organize."""

from datetime import datetime, timedelta

import streamlit as st

from .classes.sport_event import SportEvent
from .classes.sport_location import SportLocation

SPORTS_EVENTS = {
    # Monday events
    "basketball": SportEvent(
        name="Basketball",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=SportLocation.tum_courts,
        organizer_names=["Juan"],
        icon="🏀",  # ":basketball:",
        min_player_val=8,
        num_players_per_subteam=5,
        conflicting_sports=["volleyball"],
    ),
    "running_sprints": SportEvent(
        name="Running/Sprints",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.tum_courts,
        organizer_names=["Zsofi", "William"],
        icon="🏃‍♂️",  # ":running:",
        min_player_val=3,
        num_players_per_subteam=1,
        num_subteams=3,
    ),
    "volleyball": SportEvent(
        name="Volleyball",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=SportLocation.tum_courts,
        organizer_names=["Benny", "Fabi"],
        icon="🏐",  # ":volleyball:",
        min_player_val=8,
        num_players_per_subteam=4,
        num_subteams=2,
        num_pitches=2,
        conflicting_sports=["basketball"],
    ),
    # Tuesday events
    "chess": SportEvent(
        name="Chess",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.mpa_common_room,
        organizer_names=["David"],
        icon="♟️",  # ":chess_pawn:",
        min_player_val=3,
        num_players_per_subteam=1,
        num_subteams=3,
    ),
    "football": SportEvent(
        name="Football",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.ipp_courts,
        organizer_names=["Matteo"],
        icon="⚽",  # ":soccer:",
        min_player_val=11,
        num_players_per_subteam=10,
        conflicting_sports=["tennis"],
    ),
    "tennis": SportEvent(
        name="Tennis",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.ipp_courts,
        organizer_names=["???"],
        icon="🎾",  # ":tennis:",
        min_player_val=4,
        num_players_per_subteam=1,
        num_subteams=3,
        conflicting_sports=["football"],
    ),
    # Thursday events
    "capture_the_flag": SportEvent(
        name="Capture the flag",
        start=datetime(2024, 5, 2, 18, 00),
        end=datetime(2024, 5, 2, 19, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.tum_courts,
        organizer_names=["Benny", "Zsofi"],
        icon="🚩",  # ":triangular_flag_on_post:",
        min_player_val=8,
        num_players_per_subteam=8,
        num_pitches=1,
        num_matches_per_subteam=1,
    ),
    "spikeball": SportEvent(
        name="Spikeball",
        start=datetime(2024, 5, 2, 17, 30),
        end=datetime(2024, 5, 2, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.ipp_courts,
        organizer_names=["Fabi"],
        icon="🌕",  # ":full_moon:",
        min_player_val=4,
        num_players_per_subteam=2,
        num_subteams=4,
        num_pitches=3,
    ),
    # Friday events
    "beer_pong": SportEvent(
        name="Beer Pong",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        match_duration=timedelta(minutes=15),
        loc=SportLocation.mpa_common_room,
        organizer_names=["Benny", "William"],
        icon="🍺",  # ":beer:",
        min_player_val=6,
        num_players_per_subteam=2,
        num_subteams=3,
    ),
    "fooseball": SportEvent(
        name="Fooseball",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.mpa_common_room,
        match_duration=timedelta(minutes=15),
        organizer_names=["Matteo"],
        icon="💥",  # ":boom:",
        min_player_val=4,
        num_players_per_subteam=2,
        num_subteams=4,
    ),
    "ping_pong": SportEvent(
        name="Ping Pong",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.tum_courts,
        match_duration=timedelta(minutes=15),
        organizer_names=["Fabi", "Zsofi"],
        icon="⚪",  # ":white_circle:",
        min_player_val=4,
        num_players_per_subteam=1,
        num_subteams=16,
    ),
}
# for event in SPORTS_EVENTS.values():
#     fpath = DATAPATH.joinpath(f"sport_descriptions/{event.sanitized_name}.md")
#     if not fpath.exists():
#         fpath.write_text("NO DESCRIPTION YET\n## Rules\n\n## Format")
