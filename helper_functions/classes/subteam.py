from dataclasses import dataclass


@dataclass
class Subteam:
    """A subteam of a given team."""

    sport: str
    """The sanitized sport name."""

    main_team_letter: str
    """The letter of the team this subteam belongs to."""

    sub_key: str
    """The key of this subteam. Should be an integer, or 'R' for reserve."""

    players: list[str]
    """The nicknames of the players belonging to this sub-team."""

    @property
    def full_key(self) -> str:
        return f"{self.main_team_letter}_{self.sub_key}"
