import pandas as pd

from ..constants import DATAPATH


def generate_anonymous_names(number: int) -> list[str]:
    """Generate random names from a list of adjectives and animals."""
    animal_fpath = DATAPATH.joinpath("hidden/animals.csv")
    adjective_fpath = DATAPATH.joinpath("hidden/adjectives.csv")
    animals = pd.read_csv(animal_fpath, comment="#", index_col=0)
    # Remove long animal names
    animals = animals[animals["name"].str.split().str.len() == 1]
    adjectives = pd.read_csv(adjective_fpath, comment="#", names=["adjective"])
    adjs = (
        adjectives["adjective"].sample(number, replace=False, random_state=42).tolist()
    )
    animals_ = animals["name"].sample(number, replace=False, random_state=42).tolist()
    return [f"{adj.capitalize()} {animal}" for adj, animal in zip(adjs, animals_)]
