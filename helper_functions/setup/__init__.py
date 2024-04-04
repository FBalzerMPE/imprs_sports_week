"""The setup sub-module contains functions used for setting up the main player
dataframe, the teams, the sub-teams, and the schedules for each sport.
"""

from .sanitize_responses import sanitize_and_anonymize_data
from .team_creation import create_teams

__all__ = ["sanitize_and_anonymize_data", "create_teams"]
