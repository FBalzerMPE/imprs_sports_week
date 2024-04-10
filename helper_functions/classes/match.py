from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, time

from ..setup.setup_util import get_real_player_name

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
        cls, df_entry: pd.Series, all_subteams: dict[str, Subteam]
    ) -> Match:
        sport = df_entry["sport"]
        duration = timedelta(seconds=df_entry["duration"])
        subteam_a = all_subteams[sport + "_" + df_entry["team_a_key"]]
        subteam_b = all_subteams[sport + "_" + df_entry["team_b_key"]]
        return cls(
            sport=sport,
            start=df_entry["start"],
            duration=duration,
            subteam_a=subteam_a,
            subteam_b=subteam_b,
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

    @property
    def match_key(self):
        return (
            self.sport + "_" + self.subteam_a.full_key + "_" + self.subteam_b.full_key
        )
    
    @property
    def description(self) -> str:
        if self.sport == "running_sprints":
            return "various events against all other players between *17:30* and *18:30*"
        text =  f"*{self.start.strftime("%H:%M")}*: **{self.subteam_a.key_or_single} vs. {self.subteam_b.key_or_single}**"
        if self.sport == "ping_pong":
            name_a, name_b = [get_real_player_name(player) for player in self.involved_players]
            text = text.replace(" vs.", f" **({name_a})** vs.") + f" ({name_b})"
            text = self.start.strftime("%A") + f": {text}"
        return text

    def contains_player(self, player_name: str) -> bool:
        """Whether this match contains the given player (nickname expected)"""
        return player_name in self.involved_players

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
        if self.sport == other.sport == "running_sprints":
            return False
        # If they do, assert whether involved players overlap:
        intersect = set(self.involved_players).intersection(other.involved_players)
        if len(intersect) == 0:
            return False
        if verbose:
            print(
                f"{self.match_key}, {other.match_key}: {intersect} have conflicting schedules."
            )
        return True

    def get_buffered_timetuple(
        self, buffer_in_minutes: int = 0
    ) -> tuple[datetime, datetime]:
        """Return the start and end time of this match, buffered by some transition time"""
        delta = timedelta(minutes=buffer_in_minutes)
        return self.start - delta, self.end + delta

    def switch_with_other(self, other: Match, verbose: bool = False):
        """Switch this match with another one."""
        assert self.sport == other.sport, "Can only switch matches of the same sport"
        self.location, other.location = other.location, self.location
        self.start, other.start = other.start, self.start
        if verbose:
            print(f"Switched {self.match_key} with {other.match_key}")

    def set_time_and_loc(self, hour: int, minute: int, loc: str):
        """Set a new time and location for this event."""
        assert 17 <= hour <= 22
        self.start = datetime.combine(self.start.date(), time(hour, minute))
        self.location = loc
