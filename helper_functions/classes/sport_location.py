from enum import Enum


class SportLocation(Enum):
    """The locations possible."""

    tum_courts = 1

    ipp_courts = 2

    mpa_common_room = 3

    @property
    def titledName(self) -> str:
        return self.name.replace("_", " ").title()
