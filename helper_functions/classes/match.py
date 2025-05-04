from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

import pandas as pd

from ..constants import DATAPATH
from ..logger import LOGGER
from ..setup.setup_util import get_real_player_name
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
        cls, df_entry: pd.Series, all_subteams: dict[str, Subteam], silent: bool = False
    ) -> Match:
        sport = df_entry["sport"]
        key_a = df_entry["team_a_key"].replace(": ", "")
        key_b = df_entry["team_b_key"].replace(": ", "")
        full_subkey_a = sport + "_" + key_a
        full_subkey_b = sport + "_" + key_b
        duration = timedelta(seconds=df_entry["duration"])
        if sport in ["ping_pong", "tennis", "chess"]:
            default_a = Subteam(sport, key_a[0], key_a[1:], [])
            default_b = Subteam(sport, key_b[0], key_b[1:], [])
            subteam_a = all_subteams.get(full_subkey_a, default_a)
            subteam_b = all_subteams.get(full_subkey_b, default_b)
        else:
            subteam_a = all_subteams[full_subkey_a]
            subteam_b = all_subteams[full_subkey_b]
        if not silent:
            if len(subteam_a.players) == 0:
                LOGGER.debug(f"For match {sport}: {key_a}: No player found")
            if len(subteam_b.players) == 0:
                LOGGER.debug(f"For match {sport}: {key_b}: No player found")
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
            "full_key": self.match_key,
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
    def weekday(self) -> str:
        """The weekday this match takes part on."""
        return self.start.strftime("%A").lower()

    @property
    def match_key(self):
        """The unique match key for this match, including sport and subteam keys."""
        return (
            self.sport + "_" + self.subteam_a.short_key + "_" + self.subteam_b.short_key
        )

    @property
    def description(self) -> str:
        if self.sport == "running_sprints":
            return (
                "various events against all other players between *17:30* and *18:30*"
            )
        loc = "" if self.sport == "ping_pong" else f" (loc: {self.location})"
        text = f"*{self.start.strftime("%H:%M")}*{loc}: **{self.subteam_a.key_or_single} vs. {self.subteam_b.key_or_single}**"
        if self.sport == "ping_pong":
            text = self.start.strftime("%A") + f", {text}"
            if not DATAPATH.joinpath("hidden").exists():
                return text
            name_a = (
                get_real_player_name(self.subteam_a.players[0])
                if len(self.subteam_a.players) > 0
                else "DROPOUT (t.b.replaced)"
            )
            name_b = (
                get_real_player_name(self.subteam_b.players[0])
                if len(self.subteam_b.players) > 0
                else "DROPOUT (t.b.replaced)"
            )
            text = text.replace(" vs.", f" **({name_a})** vs.") + f" ({name_b})"
        return text

    @property
    def winning_players(self) -> list[str]:
        if self.winner != "" and self.winner in ["A", "B", "C"]:
            if self.subteam_a.main_team_letter == self.winner:
                return self.subteam_a.players
            elif self.subteam_b.main_team_letter == self.winner:
                return self.subteam_b.players
            else:
                LOGGER.info(f"Unrecognized winning team for '{self.match_key}'")
        return []

    @property
    def tying_players(self) -> list[str]:
        if self.winner in ["AB", "AC", "BC"]:
            return self.involved_players
        return []

    def get_desc_with_real_names(self) -> str:
        """Retrieve the description, typing out the full teams' attendances."""
        text = f"*{self.start.strftime("%H:%M")}*: "
        text += f"**{self.subteam_a.full_key} ({self.subteam_a.real_names})\\\n"
        text += f"vs. {self.subteam_b.full_key} ({self.subteam_b.real_names})**"
        return text

    def contains_player(self, player_name: str) -> bool:
        """Whether this match contains the given player (nickname expected)"""
        return player_name in self.involved_players

    def get_calendar_entry(self, identity: str) -> dict[str, str]:
        """Generate a calendar entry"""
        try:
            index = int(self.location) - 1
        except ValueError:
            index = 0
        title = f"{index + 1}::  {self.subteam_a.full_key} vs {self.subteam_b.full_key}".replace(
            ": ", ""
        )
        colors = ["#8B0000", "#00008B", "#B8860B", "#C10210", "#008B00", "#008B8B"]
        if index >= len(colors):
            LOGGER.warning("Not enough colors to display courts in schedule")
            index = len(colors) - 1
        color = colors[index]
        return {
            "title": title,
            "start": self.start.isoformat(),
            "end": (self.start + self.duration).isoformat(),
            "resourceId": identity,
            "color": color,
            "borderColor": "black",
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
            my_start = self.start.strftime("%H:%M, %A")
            other_start = other.start.strftime("%H:%M, %A")
            p_team = [
                team.main_team_letter
                for player in intersect
                for team in (self.subteam_a, self.subteam_b)
                if player in team.players
            ][0]
            LOGGER.warning(
                f"{self.match_key}, {other.match_key}: {intersect} ({p_team}) have conflicting schedules ({my_start}, {other_start})."
            )
        return True

    def get_buffered_timetuple(
        self, buffer_in_minutes: int = 0
    ) -> tuple[datetime, datetime]:
        """Return the start and end time of this match, buffered by some transition time"""
        delta = timedelta(minutes=buffer_in_minutes)
        return self.start - delta, self.end + delta

    def switch_with_other(self, other: Match):
        """Switch this match with another one."""
        assert self.sport == other.sport, "Can only switch matches of the same sport"
        self.location, other.location = other.location, self.location
        self.start, other.start = other.start, self.start
        LOGGER.info(f"Switched {self.match_key} with {other.match_key}")

    def set_time_and_loc(self, hour: int, minute: int, loc: str):
        """Set a new time and location for this event."""
        assert 17 <= hour <= 22
        self.start = datetime.combine(self.start.date(), time(hour, minute))
        self.location = loc
