"""The setup sub-module contains functions used for setting up the main player
dataframe, the teams, the sub-teams, and the schedules for each sport.
"""

from .sanitize_responses import generate_anonymous_names, sanitize_and_anonymize_data
from .sanitize_old_responses import sanitize_and_anonymize_data_2024
from .subteam_creation import generate_all_subteams, try_switch_players
from .team_creation import create_teams

__all__ = [
    "generate_anonymous_names",
    "sanitize_and_anonymize_data",
    "create_teams",
    "generate_all_subteams",
    "try_switch_players",
    "sanitize_and_anonymize_data_2024",
]
