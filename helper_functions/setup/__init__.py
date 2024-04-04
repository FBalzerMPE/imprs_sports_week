"""The setup sub-module contains functions used for setting up the main player
dataframe, the teams, the sub-teams, and the schedules for each sport.
"""

from .subteam_creation import generate_subteams_for_sport
from .sanitize_responses import generate_anonymous_names, sanitize_and_anonymize_data
from .team_creation import create_teams

__all__ = [
    "generate_anonymous_names",
    "sanitize_and_anonymize_data",
    "create_teams",
    "generate_subteams_for_sport",
]
