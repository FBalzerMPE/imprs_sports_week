from dataclasses import dataclass

import pandas as pd


@dataclass
class SportLocation:
    """The locations possible."""

    key: str
    """The name of this location."""

    latitude: float
    """The latitude of this location."""

    longitude: float
    """The longitude of this location."""

    display_name: str
    """How this location should be displayed on the map."""

    description: str = ""
    """The description of this location."""

    @property
    def as_series(self) -> pd.Series:
        return pd.Series(
            {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "size": 3,
                "name": self.key,
                "display_name": self.display_name,
                "description": self.description,
            }
        )
