from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd

from .subteam import Subteam


@dataclass
class Match:
    """Describes a match between two subteams, including time, location, and sport."""

    sport: str
    """The sport this match is associated with."""

    start: datetime
    """The datetime when the match takes place."""

    duration: timedelta
    """The approximate planned duration of the match."""

    subteam_a: Subteam
    """The first subteam that is playing."""

    subteam_b: Subteam
    """The second subteam that is playing."""

    location: str
    """The court or pitch or table where this match takes place."""

    result: str = ""
    """The result of this match, deliberately left as string as it can 
    vary from sport to sport.."""

    winner: str = ""
    """The subteam key that won this match."""

    @classmethod
    def from_dataframe_entry(
        cls, df_entry: pd.Series, all_subteams: list[Subteam]
    ) -> Match:
        sport = df_entry["sport"]
        duration = timedelta(seconds=df_entry["duration"])
        subteams = {
            subteam.full_key: subteam
            for subteam in all_subteams
            if subteam.sport == sport
        }
        return cls(
            sport=sport,
            start=df_entry["start"],
            duration=duration,
            subteam_a=subteams[df_entry["team_a_key"]],
            subteam_b=subteams[df_entry["team_b_key"]],
            location=df_entry["location"],
            result=df_entry["result"],
            winner=df_entry["winner"],
        )

    @property
    def as_series(self) -> pd.Series:
        series_dict = {
            "sport": self.sport,
            "team_a": self.subteam_a.key_or_single,
            "team_b": self.subteam_b.key_or_single,
            "location": self.location,
            "day": self.start.strftime("%A"),
            "time": self.start.strftime("%H:%M"),
            "result": self.result,
            "winner": self.winner,
            "start": self.start,
            "duration": self.duration.seconds,
            "team_a_key": self.subteam_a.full_key,
            "team_b_key": self.subteam_b.full_key,
        }
        return pd.Series(series_dict)

    @property
    def involved_players(self):
        return self.subteam_a.players + self.subteam_b.players

    @property
    def end(self):
        return self.start + self.duration

    def get_calendar_entry(self) -> dict[str, str]:
        """Generate a calendar entry"""
        title = f"{self.subteam_a.full_key} vs {self.subteam_b.full_key}"
        return {
            "title": title,
            "start": self.start.isoformat(),
            "end": (self.start + self.duration).isoformat(),
            "resourceId": self.sport,
            "color": "green",
        }

    def has_hard_collision(self, other: Match, verbose=False) -> bool:
        """Check whether this match has a hard collision with another match
        at the same time due to the same players being involved in both.
        """
        # First, assert whether the time windows overlap at all:
        if self.start >= other.end or self.end <= other.start:
            return False
        # If they do, assert whether involved players overlap:
        intersect = set(self.involved_players).intersection(other.involved_players)
        if len(intersect) == 0:
            return False
        if verbose:
            print(
                f"{self.sport}, {other.sport}: {intersect} have conflicting schedules."
            )
        return True
