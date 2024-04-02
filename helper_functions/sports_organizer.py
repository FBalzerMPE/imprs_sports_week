from dataclasses import dataclass


@dataclass
class SportsOrganizer:
    """A person responsible for organizing a sports event."""

    name: str
    """The name of the organizer."""

    email: str
    """The email of the organizer."""

    sport_keys: list[str]
    """The key for the sports that are organized by this person."""
