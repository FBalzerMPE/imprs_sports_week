import pandas as pd

from .constants import DATAPATH, SPORTS_DF


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


def sanitize_and_anonymize_data(rerun=False) -> pd.DataFrame:
    """
    Sanitizes and anonymizes the data by removing all columns that are not needed for the analysis.
    """
    backup_fpath = DATAPATH.joinpath("sanitized_responses.csv")
    if backup_fpath.exists() and not rerun:
        df = pd.read_csv(backup_fpath)
        return df
    fpath = DATAPATH.joinpath("hidden/form_responses_2024_03_28.csv")
    cols = [
        "response_timestamp",
        "name",
        "institute",
        "phd_or_postdoc",
        "time_available",
        "events_interested_in",
    ]
    df = pd.read_csv(fpath, names=list(cols), skiprows=1, dtype=str)
    df["is_phd"] = df.phd_or_postdoc.fillna("").apply(lambda x: "phd" in x.lower())
    df["is_postdoc"] = df.phd_or_postdoc.fillna("").apply(
        lambda x: "postdoc" in x.lower()
    )
    assert all(df["is_phd"] == ~df["is_postdoc"]), "Some rows have bad phd/postdoc data"
    df["response_timestamp"] = pd.to_datetime(
        df["response_timestamp"], format="%d/%m/%Y %H:%M:%S"
    )
    # Fix the institute names
    proper_institute_map = {
        "Max Planck Institute for Plasma Physics": "IPP",
        "MPI for Plasma Physics": "IPP",
        "Max Planck IPP (TOK)": "IPP",
        "Plasmaphysik": "IPP",
        "European Southern Observatory": "ESO",
        "MPE / LMU": "MPE",
        "USM / LMU": "USM",
        "MPE / USM": "MPE",
        "ESO and TUM": "ESO",
        "ESO / University of Milan": "ESO",
        "The Max Planck Institute for Astrophysics": "MPA",
        "University Observatory Ludwig-Maximilians University of Munich": "USM",
        "HM": "USM",
    }
    df["institute"] = df.institute.replace(proper_institute_map).str.upper().str.strip()

    for _, (sport, prop_name) in SPORTS_DF[["name", "proper_name"]].iterrows():
        df[sport] = df.events_interested_in.fillna("").str.contains(
            prop_name, case=False
        )
    df["num_sports"] = df[SPORTS_DF["name"].tolist()].sum(axis=1).astype(int)
    for day in ["monday", "tuesday", "thursday", "friday"]:
        df["avail_" + day] = df.time_available.fillna("").str.contains(day, case=False)
    df["late_entry"] = df.response_timestamp > pd.Timestamp("2024-03-31 12:00:00")
    deletable_cols = [
        "name",
        "phd_or_postdoc",
        "is_phd",
        "events_interested_in",
        "time_available",
        "response_timestamp",
    ]
    df = df[[col for col in df.columns if col not in deletable_cols]]
    df.insert(0, "nickname", generate_anonymous_names(len(df)))
    df.to_csv(backup_fpath, index=False)
    return df
