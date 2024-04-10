"""Contains all of the events that we are planning to organize."""

from datetime import datetime, timedelta

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
        pitch_type_name="Court",
        organizer_names=["Juan"],
        icon="🏀",  # ":basketball:",
        min_player_val=8,
        num_players_per_subteam=4,
        conflicting_sports=["volleyball"],
    ),
    "running_sprints": SportEvent(
        name="Running/Sprints",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 18, 30),
        match_duration=timedelta(minutes=60),
        loc=SportLocation.ipp_courts,
        pitch_type_name="Court",
        organizer_names=["Zsofi", "William"],
        icon="🏃‍♂️",  # ":running:",
        min_player_val=3,
        num_players_per_subteam=4,
        num_subteams=1,
    ),
    "volleyball": SportEvent(
        name="Volleyball",
        start=datetime(2024, 4, 29, 17, 45),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=SportLocation.tum_courts,
        pitch_type_name="Court",
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
        match_duration=timedelta(minutes=40),
        loc=SportLocation.mpa_common_room,
        pitch_type_name="Board",
        organizer_names=["David"],
        icon="♟️",  # ":chess_pawn:",
        num_pitches=3,
        min_player_val=3,
        num_players_per_subteam=1,
        num_subteams=3,
    ),
    "football": SportEvent(
        name="Football",
        start=datetime(2024, 4, 30, 17, 45),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=SportLocation.ipp_courts,
        pitch_type_name="Pitch",
        organizer_names=["Matteo G"],
        icon="⚽",  # ":soccer:",
        min_player_val=11,
        num_players_per_subteam=8,
        conflicting_sports=["tennis"],
    ),
    "tennis": SportEvent(
        name="Tennis",
        start=datetime(2024, 4, 30, 17, 45),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=SportLocation.ipp_courts,
        pitch_type_name="Court",
        organizer_names=["Matteo B"],
        icon="🎾",  # ":tennis:",
        min_player_val=4,
        num_players_per_subteam=1,
        num_subteams=3,
        num_pitches=3,
        conflicting_sports=["football"],
    ),
    # Thursday events
    "capture_the_flag": SportEvent(
        name="Capture the flag",
        start=datetime(2024, 5, 2, 17, 45),
        end=datetime(2024, 5, 2, 18, 45),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.ipp_courts,
        pitch_type_name="Court",
        organizer_names=["Benny", "Zsofi"],
        icon="🚩",  # ":triangular_flag_on_post:",
        min_player_val=8,
        num_players_per_subteam=8,
        num_pitches=1,
        num_matches_per_subteam=1,
    ),
    "spikeball": SportEvent(
        name="Spikeball",
        start=datetime(2024, 5, 2, 17, 45),
        end=datetime(2024, 5, 2, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=SportLocation.ipp_courts,
        pitch_type_name="Net no.",
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
        match_duration=timedelta(minutes=20),
        loc=SportLocation.mpa_common_room,
        pitch_type_name="Table",
        organizer_names=["Benny", "William"],
        icon="🍺",  # ":beer:",
        num_pitches=2,
        min_player_val=6,
        num_players_per_subteam=3,
        num_subteams=3,
        conflicting_sports=["foosball"],
    ),
    "foosball": SportEvent(
        name="Foosball",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.mpa_common_room,
        pitch_type_name="Table",
        match_duration=timedelta(minutes=15),
        organizer_names=["Matteo G"],
        icon="💥",  # ":boom:",
        min_player_val=4,
        num_players_per_subteam=2,
        num_subteams=4,
        conflicting_sports=["beer_pong"],
    ),
    "ping_pong": SportEvent(
        name="Ping Pong",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=SportLocation.tum_courts,
        pitch_type_name="Table",
        match_duration=timedelta(minutes=15),
        organizer_names=["Fabi", "Zsofi"],
        icon="⚪",  # ":white_circle:",
        min_player_val=4,
        num_pitches=2,
        num_players_per_subteam=1,
        num_subteams=16,
    ),
}
# for event in SPORTS_EVENTS.values():
#     fpath = DATAPATH.joinpath(f"sport_descriptions/{event.sanitized_name}.md")
#     if not fpath.exists():
#         fpath.write_text("NO DESCRIPTION YET\n## Rules\n\n## Format")
