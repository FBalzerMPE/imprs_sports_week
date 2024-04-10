from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd

from ..constants import ALL_DAYS, SPORTS_LIST
from .match import Match


@dataclass
class Player:
    nickname: str
    """The nickname of this player."""

    avail_days: list[str]
    """The days where this player is available."""

    main_team_letter: str
    """The team this player is part of."""

    subteams: dict[str, str]
    """The subteams this player is part of."""

    matches: list[Match] = field(repr=False)
    """The matches this player is part of."""

    @classmethod
    def from_series(cls, series: pd.Series, all_matches: list[Match]) -> Player:
        name = series["nickname"]
        avail_days = [day for day in ALL_DAYS if series[f"avail_{day}"]]
        team = series["Team"].replace("Team ", "")
        subteams = {
            sport: f"{team}: {subteam}"
            for sport in SPORTS_LIST
            if (subteam := series[f"subteam_{sport}"]) != ""
        }
        matches = [match_ for match_ in all_matches if match_.contains_player(name)]
        matches = sorted(matches, key=lambda match_: match_.start)
        return cls(
            nickname=name,
            avail_days=avail_days,
            main_team_letter=team,
            subteams=subteams,
            matches=matches,
        )

    def match_times(self) -> list[tuple[datetime, datetime]]:
        return [(match_.start, match_.end) for match_ in self.matches]

    def get_schedule(self) -> str:
        from ..data_registry import ALL_SUBTEAMS
        from ..sport_event_registry import SPORTS_EVENTS

        text = "Schedule:\n\n"

        for sport, subteam_key in self.subteams.items():
            event = SPORTS_EVENTS[sport]
            subteam = ALL_SUBTEAMS[sport + "_" + subteam_key]
            subteam_key = f"**{subteam_key}**"
            matches = [match for match in self.matches if match.sport == sport]
            vals, ind = np.unique(
                [match_.start.strftime("%A") for match_ in matches], return_index=True
            )

            days = vals[np.argsort(ind)]
            if subteam.is_reserve:
                days = event.days
            days = ", ".join([day.capitalize() for day in days])
            text += f"**{event.icon} {event.name} ({days}):**\\\n"
            if subteam.is_reserve:
                text += "You are scheduled to be a reserve player. "
                if sport in ["spikeball", "tennis", "table_tennis", "fooseball"]:
                    text += "This means that you might receive a late call to join if one of your teammates cannot make it."
                else:
                    if event.num_subteams > 1:
                        text += "This means that you may still choose a subteam to support, and may be substituted in during the games."
                    else:
                        text += "This means that you still may join the event and be substituted in during the games."
            else:
                if event.num_players_per_subteam == 1:
                    text += (
                        f"You will be competing on your own in two separate matches:"
                    )
                else:
                    other_players = [
                        player for player in subteam.players if player != self.nickname
                    ]
                    if event.num_players_per_subteam > 2:
                        other_player_str = (
                            ", ".join(other_players[:-1]) + " and " + other_players[-1]
                        )
                    else:
                        other_player_str = other_players[-1]
                    text += f"You are part of subteam {subteam_key}, together with *{other_player_str}*.\\\nYour matches are:"
                text += "\\\n"
                if sport == "running_sprints":
                    text += f"You are scheduled to attend {matches[0].description}.\n"
                else:
                    text += f"\t{matches[0].description}, and\\\n\t{matches[1].description}\n"
            text += "\n\n"
        return text
