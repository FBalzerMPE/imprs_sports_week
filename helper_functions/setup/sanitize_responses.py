from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import yaml

from ..constants import CURRENT_YEAR, FpathRegistry
from ..logger import LOGGER
from .nickname_generation import generate_anonymous_names


def _get_ping_pong_days(events: str):
    event_list = events.split(";")
    return [day.split()[3].lower() for day in event_list if day.startswith("Ping Pong")]


def _add_event_info(df: pd.DataFrame) -> pd.DataFrame:
    """Add sport event information to the dataframe, as well as the number of
    sports a player is interested in."""
    from ..data_registry import DATA_NOW

    for event in DATA_NOW.sport_events.values():
        event_name = event.sanitized_name
        is_interested = (
            df["events_interested_in"]
            .fillna("")
            .str.replace(" ", "_")
            .str.replace("/", "_")
            .str.lower()
            .str.replace("foose", "foos")
            .str.contains(event_name)
        )
        df[event.sanitized_name] = is_interested
    ping_pong_days = df["events_interested_in"].apply(_get_ping_pong_days)
    df["ping_pong_days"] = ping_pong_days
    df["ping_pong"] = ping_pong_days.apply(lambda x: len(x) > 0)
    df["num_sports"] = df[DATA_NOW.sport_events.keys()].sum(axis=1).astype(int)
    return df


def _load_payment_info() -> dict[str, str]:
    fpath = FpathRegistry.get_path_hidden().joinpath("money_received.yml")
    responses = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    return {e["name"]: e["receiver"] for e in responses}


def _add_payment_info(df: pd.DataFrame) -> pd.DataFrame:
    p_info = _load_payment_info()
    df["has_paid_fee"] = df["name"].apply(lambda x: x in p_info)
    unrecognized = [
        n.split()[0][:2] + n.split()[1][:2]
        for n in p_info
        if n not in df["name"].tolist()
    ]
    if len(unrecognized) > 0:
        LOGGER.warning(
            f"Could not find the following people that payment was received from. Please check their names: {unrecognized}"
        )
    return df


def _get_single_name(
    row: pd.Series, nick_dict: dict[str, str], new_nicknames: list[str]
) -> str:
    """Get a single name for a row. Mutates the new_nicknames list, removing nicknames taken."""
    if row["wants_new_avatar"]:
        return new_nicknames.pop(0)
    if row["name"] not in nick_dict.keys():
        LOGGER.warning(f"Name {row['name']} not found in old nicknames.")
        return new_nicknames.pop(0)
    return nick_dict[row["name"]]


def get_nicknames_2025_column(df: pd.DataFrame) -> pd.Series:
    """Add nicknames to the dataframe."""
    from ..data_registry import DATA_2024

    old_nicknames = DATA_2024.nickname_to_name_df
    nick_dict = old_nicknames.set_index("name")["nickname"].to_dict()
    # The first 120 nicknames are already taken for last year
    new_nicknames = generate_anonymous_names(120 + len(df))[120:]
    return df.apply(lambda row: _get_single_name(row, nick_dict, new_nicknames), axis=1)


def sanitize_and_anonymize_data(
    overwrite=False,
    anonymize=True,
    year=CURRENT_YEAR,
    response_path: Literal["latest"] | Path = "latest",
) -> pd.DataFrame:
    """
    Sanitizes and anonymizes the data by removing all columns that are not needed for the analysis.

    Parameters
    ----------
    overwrite : bool, optional
        Whether to overwrite the sanitized data, by default False
    anonymize : bool, optional
        Whether to anonymize the returned data, by default True
    year : int, optional
        The year of the data, by default CURRENT_YEAR
    response_path : Literal["latest"] | Path, optional
        The path to the responses, by default "latest"

    Returns
    -------
    pd.DataFrame
        The sanitized and dataframe, anonymized if wished.
    """

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
        "email",
        "institute",
        "status",
        "events_interested_in",
        "assets_brought",
        "avatar_request",
        "picture_consent",
        "feedback",
    ]
    # Do this in case there are additional columns we don't need:
    num_cols = len(pd.read_csv(response_path, dtype=str).columns)
    cols = [cols[i] if i < len(cols) else str(i) for i in range(num_cols)]
    # Load the df:
    df = pd.read_csv(response_path, names=cols, usecols=cols[:8], skiprows=1, dtype=str)
    df["wants_new_avatar"] = (
        df["avatar_request"]
        .fillna("")
        .apply(lambda x: not x.startswith("Yes I attended and I want to keep"))
    )
    df["attended_before"] = df["avatar_request"].fillna("").str.startswith("Yes")
    df["nickname"] = get_nicknames_2025_column(df)
    df["response_timestamp"] = pd.to_datetime(
        df["response_timestamp"].str.split().apply(lambda x: x[:2]).str.join(" "),
        format="%d/%m/%Y %H:%M:%S",
    )
    df = _add_event_info(df)
    df["late_entry"] = df.response_timestamp > pd.Timestamp("2025-04-10 12:00:00")
    df = _add_payment_info(df)
    if overwrite:
        df.to_csv(FpathRegistry.get_path_responses(year, sanitized=False), index=False)
    df["confirmation_status"] = False
    deletable_cols = [
        "name",
        "events_interested_in",
        "time_available",
        "response_timestamp",
        "avatar_request",
        "wants_new_avatar",
        "email",
    ]
    nick_cols = ["nickname", "name", "institute", "status", "confirmation_status"]
    col_map = {col: f"{col.replace("_", " ").capitalize():25s}" for col in nick_cols}
    col_map["confirmation_status"] = "Has replied"
    path_base = FpathRegistry.get_path_hidden()
    nickname_df: pd.DataFrame = df[nick_cols].sort_values("nickname")
    (
        nickname_df.map(lambda x: str(x).ljust(25, " "))
        .rename(columns=col_map)
        .to_csv(path_base.joinpath("nickname_to_name.txt"), index=False, sep="\t")
    )
    nickname_df.to_csv(path_base.joinpath("nickname_to_name.csv"), index=False)
    try:
        nickname_df.to_excel(path_base.joinpath("nickname_to_name.xlsx"), index=False)
    except ModuleNotFoundError:
        print("Didn't write to excel as openpyxl was missing.")
    anon_df = df[[col for col in df.columns if col not in deletable_cols]]
    anon_df.to_csv(backup_fpath, index=False)
    if anonymize:
        return anon_df
    return df
