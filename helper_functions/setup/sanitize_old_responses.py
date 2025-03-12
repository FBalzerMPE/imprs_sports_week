from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from ..constants import CURRENT_YEAR, DATAPATH, FpathRegistry
from .nickname_generation import generate_anonymous_names


def sanitize_and_anonymize_data_2024(
    overwrite=False,
    anonymize=True,
    verbose: bool = True,
    year=CURRENT_YEAR,
    response_path: Literal["latest"] | Path = "latest",
) -> pd.DataFrame:
    """
    Sanitizes and anonymizes the data by removing all columns that are not needed for the analysis.
    """

    from ..data_registry import DATA_NOW

    backup_fpath = FpathRegistry.get_path_responses(year)
    if backup_fpath.exists() and not overwrite and anonymize:
        df = pd.read_csv(backup_fpath)
        return df
    if response_path == "latest":
        response_path = FpathRegistry.get_path_responses(sanitized=False, latest=True)
    assert response_path.exists(), f"Path {response_path} does not exist."
    # fpath = DATAPATH.joinpath("hidden/form_responses_2024_04_23.csv")
    cols = [
        "response_timestamp",
        "name",
        "institute",
        "phd_or_postdoc",
        "time_available",
        "events_interested_in",
        "email",
        "confirmation_status",
    ]
    # Do this in case there are additional columns we don't need:
    num_cols = len(pd.read_csv(response_path, dtype=str).columns)
    cols = [cols[i] if i < len(cols) else str(i) for i in range(num_cols)]
    # Load the df:
    df = pd.read_csv(response_path, names=cols, usecols=cols[:8], skiprows=1, dtype=str)
    df["is_phd"] = df.phd_or_postdoc.fillna("").apply(lambda x: "phd" in x.lower())
    df["is_postdoc"] = df.phd_or_postdoc.fillna("").apply(
        lambda x: "postdoc" in x.lower()
    )
    assert all(df["is_phd"] == ~df["is_postdoc"]), "Some rows have bad phd/postdoc data"
    df["confirmation_status"] = df.confirmation_status.fillna("").apply(
        lambda x: "yes" in x.lower()
    )
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
        "MPI for plasma physics": "IPP",
        "Max Planck Institute for Extraterrestrial Physics": "MPE",
    }
    df["institute"] = df.institute.replace(proper_institute_map).str.upper().str.strip()

    for day in ["monday", "tuesday", "thursday", "friday"]:
        df["avail_" + day] = df.time_available.fillna("").str.contains(day, case=False)
    if verbose:
        print("Interested in the following sports, but not available:")
    for event in DATA_NOW.sport_events.values():
        event_name = (
            "Running/Sprints"
            if event.sanitized_name == "running_sprints"
            else event.name
        )
        is_interested = df.events_interested_in.fillna("").str.contains(
            event_name.replace("Foos", "Foose"), case=False
        )
        is_avail = pd.DataFrame([df["avail_" + day] for day in event.days]).any(axis=0)
        df["wants_" + event.sanitized_name] = is_interested
        df[event.sanitized_name] = is_interested & is_avail
        if verbose:
            print(event.name, np.sum(~is_avail & is_interested))
    df["num_sports"] = df[DATA_NOW.sport_events.keys()].sum(axis=1).astype(int)
    df["num_sports_not_avail"] = (
        df[["wants_" + key for key in DATA_NOW.sport_events.keys()]]
        .sum(axis=1)
        .astype(int)
        - df["num_sports"]
    )
    df["late_entry"] = df.response_timestamp > pd.Timestamp("2024-04-10 12:00:00")
    df.insert(0, "nickname", generate_anonymous_names(len(df)))
    if overwrite:
        df.to_csv(FpathRegistry.get_path_responses(year, sanitized=False), index=False)
    deletable_cols = [
        "name",
        "phd_or_postdoc",
        "is_phd",
        "events_interested_in",
        "time_available",
        "response_timestamp",
        "email",
    ]
    nick_cols = ["nickname", "name", "institute", "confirmation_status"]
    col_map = {col: f"{col.replace("_", " ").capitalize():25s}" for col in nick_cols}
    col_map["confirmation_status"] = "Has replied"
    nickname_df: pd.DataFrame = df[nick_cols].sort_values("nickname")
    (
        nickname_df.map(lambda x: str(x).ljust(25, " "))
        .rename(columns=col_map)
        .to_csv(DATAPATH.joinpath("hidden/nickname_to_name.txt"), index=False, sep="\t")
    )
    nickname_df.to_csv(DATAPATH.joinpath("hidden/nickname_to_name.csv"), index=False)
    try:
        nickname_df.to_excel(
            DATAPATH.joinpath("hidden/nickname_to_name.xlsx"), index=False
        )
    except ModuleNotFoundError:
        print("Didn't write to excel as openpyxl was missing.")
    anon_df = df[[col for col in df.columns if col not in deletable_cols]]
    anon_df.to_csv(backup_fpath, index=False)
    if anonymize:
        return anon_df
    return df
