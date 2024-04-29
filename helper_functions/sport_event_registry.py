"""Contains all of the events that we are planning to organize."""

from datetime import datetime, timedelta

from .classes.sport_event import RunningEvent, SportEvent
from .classes.sport_location import SportLocation

ALL_LOCATIONS = {
    "tum_pitches": SportLocation(
        "tum_pitches",
        48.263479,
        11.668083,
        "TUM Volley- and Basketball pitches",
        "The TUM pitches used for Volleyball and Basketball",
    ),
    "ipp_tennis_courts": SportLocation(
        "ipp_tennis_courts",
        48.261604,
        11.676743,
        "IPP Courts",
        "The SV Plasma tennis courts, kindly provided to us to realize the tennis games.",
    ),
    # "ipp_big_field": SportLocation(
    #     "ipp_big_field",
    #     48.262174,
    #     11.676849,
    #     "Big IPP field (preliminary, to be confirmed!)",
    #     "Big grass football field used for Running/Sprints, Football, Capture the Flag, and Spikeball.",
    # ),
    "tum_big_field": SportLocation(
        "tum_big_field",
        48.263839,
        11.665043,
        "TUM football and running field (⚠️ new location! ⚠️)",
        "The big grass field used for Running/Sprints, Football, Capture the Flag, and Spikeball.",
    ),
    "mpe_ping_pong": SportLocation(
        "mpe_ping_pong",
        48.261563,
        11.670697,
        "PP: Table 1 (MPE)",
        "The main ping pong table, located in the basement of MPE. To access it, turn right after entering MPE, walk through to the back, turn left, follow the corridor for a few right and left turns, and finally enter the door on the left with a downward stair case right behind it.",
    ),
    "ipp_ping_pong_1": SportLocation(
        "ipp_ping_pong_1",
        48.260717,
        11.675729,
        "PP: Table 2 (IPP1)",
        "The second ping pong table. To access it, enter the building, walk straight ahead, briefly turn left to access the stair case, walk up to the first floor and enter door to the corridor to the right (there should be a table tennis sign). If the door is locked, text Fabi or Zsofi on Signal.",
    ),
    "ipp_ping_pong_2": SportLocation(
        "ipp_ping_pong_2",
        48.263171,
        11.673439,
        "PP: Table 3 (IPP2)",
        "The third ping pong table. To access it, enter through the main door and go downstairs.",
    ),
    "mpa_common_room": SportLocation(
        "mpa_common_room",
        48.261249,
        11.671584,
        "MPA common/seminar room",
        "At the basement heart of MPA, the common room provides us with a Foosball table, while the seminar room will be used for Chess and Beer Pong, and the final award ceremony. To access it, enter MPA (also possible coming from the MPE), walk by the security, take the stairs downstairs, and walk around until you hear loud voices.",
    ),
}

SPORTS_EVENTS = {
    # Monday events
    "ping_pong": SportEvent(
        name="Ping Pong",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=ALL_LOCATIONS["mpe_ping_pong"],
        pitch_type_name="Table",
        match_duration=timedelta(minutes=15),
        organizer_names=["Fabi", "Zsofi"],
        icon="⚪",  # ":white_circle:",
        min_player_val=4,
        num_pitches=2,
        num_players_per_subteam=1,
        num_subteams=16,
        point_weight_factor=2,
    ),
    "basketball": SportEvent(
        name="Basketball",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=ALL_LOCATIONS["tum_pitches"],
        pitch_type_name="Court",
        organizer_names=["Juan"],
        icon="🏀",  # ":basketball:",
        min_player_val=8,
        num_players_per_subteam=4,
        conflicting_sports=["volleyball"],
    ),
    "running_sprints": SportEvent(
        name="Running and Sprints",
        start=datetime(2024, 4, 29, 17, 30),
        end=datetime(2024, 4, 29, 19, 00),
        match_duration=timedelta(minutes=60),
        loc=ALL_LOCATIONS["tum_big_field"],
        pitch_type_name="Court",
        organizer_names=["Zsofi", "William"],
        icon="🏃",  # ":running:",
        min_player_val=3,
        num_players_per_subteam=4,
        num_subteams=1,
    ),
    "volleyball": SportEvent(
        name="Volleyball",
        start=datetime(2024, 4, 29, 17, 00),
        end=datetime(2024, 4, 29, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=ALL_LOCATIONS["tum_pitches"],
        pitch_type_name="Court",
        organizer_names=["Benny", "Fabi"],
        icon="🏐",  # ":volleyball:",
        min_player_val=8,
        num_players_per_subteam=4,
        num_subteams=2,
        num_pitches=2,
        conflicting_sports=["basketball"],
        point_weight_factor=1.5,
    ),
    # Tuesday events
    "chess": SportEvent(
        name="Chess",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=40),
        loc=ALL_LOCATIONS["mpa_common_room"],
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
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=ALL_LOCATIONS["tum_big_field"],
        pitch_type_name="Pitch",
        organizer_names=["Matteo G"],
        icon="⚽",  # ":soccer:",
        min_player_val=11,
        num_players_per_subteam=8,
        conflicting_sports=["tennis"],
        point_weight_factor=1.5,
    ),
    "tennis": SportEvent(
        name="Tennis",
        start=datetime(2024, 4, 30, 17, 30),
        end=datetime(2024, 4, 30, 21, 00),
        match_duration=timedelta(minutes=45),
        loc=ALL_LOCATIONS["ipp_tennis_courts"],
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
        start=datetime(2024, 5, 2, 17, 30),
        end=datetime(2024, 5, 2, 19, 30),
        match_duration=timedelta(minutes=30),
        loc=ALL_LOCATIONS["tum_big_field"],
        pitch_type_name="Court",
        organizer_names=["Benny", "Zsofi"],
        icon="🚩",  # ":triangular_flag_on_post:",
        min_player_val=8,
        num_players_per_subteam=8,
        num_pitches=1,
        num_matches_per_subteam=1,
        point_weight_factor=1.5,
    ),
    "spikeball": SportEvent(
        name="Spikeball",
        start=datetime(2024, 5, 2, 17, 30),
        end=datetime(2024, 5, 2, 21, 00),
        match_duration=timedelta(minutes=30),
        loc=ALL_LOCATIONS["tum_big_field"],
        pitch_type_name="Net no.",
        organizer_names=["Fabi"],
        icon="🌕",  # ":full_moon:",
        min_player_val=4,
        num_players_per_subteam=2,
        num_subteams=4,
        num_pitches=3,
        point_weight_factor=1.5,
    ),
    # Friday events
    "beer_pong": SportEvent(
        name="Beer Pong",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        match_duration=timedelta(minutes=20),
        loc=ALL_LOCATIONS["mpa_common_room"],
        pitch_type_name="Table",
        organizer_names=["Benny", "William"],
        icon="🍺",  # ":beer:",
        num_pitches=2,
        min_player_val=6,
        num_players_per_subteam=3,
        num_subteams=3,
        conflicting_sports=["foosball"],
        point_weight_factor=1.5,
    ),
    "foosball": SportEvent(
        name="Foosball",
        start=datetime(2024, 5, 3, 17, 30),
        end=datetime(2024, 5, 3, 21, 00),
        loc=ALL_LOCATIONS["mpa_common_room"],
        pitch_type_name="Table",
        match_duration=timedelta(minutes=15),
        organizer_names=["Matteo G"],
        icon="💥",  # ":boom:",
        min_player_val=4,
        num_players_per_subteam=2,
        num_subteams=4,
        conflicting_sports=["beer_pong"],
        point_weight_factor=1.5,
    ),
}
# for event in SPORTS_EVENTS.values():
#     fpath = DATAPATH.joinpath(f"sport_descriptions/{event.sanitized_name}.md")
#     if not fpath.exists():
#         fpath.write_text("NO DESCRIPTION YET\n## Rules\n\n## Format")


RUNNING_EVENTS = [
    RunningEvent(
        "Warm up", datetime(2024, 4, 29, 17, 30), datetime(2024, 4, 29, 17, 45)
    ),
    RunningEvent(
        "Sprints", datetime(2024, 4, 29, 17, 45), datetime(2024, 4, 29, 18, 5)
    ),
    RunningEvent("Relay", datetime(2024, 4, 29, 18, 5), datetime(2024, 4, 29, 18, 20)),
    RunningEvent(
        "Reaction Games", datetime(2024, 4, 29, 18, 20), datetime(2024, 4, 29, 18, 45)
    ),
    RunningEvent(
        "10-minute run", datetime(2024, 4, 29, 18, 45), datetime(2024, 4, 29, 19, 0)
    ),
]
