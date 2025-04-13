import numpy as np
import pandas as pd
import streamlit as st
from pandas.io.formats.style import Styler

from ..constants import PAGESPATH, SPORTS_LIST
from ..data_registry import DataRegistry


def _get_row_color(data: DataRegistry, row_val: str, alpha: float = 0.3) -> str:

    if not isinstance(row_val, str):
        return ""

    for team in data.teams:
        if f"{team.team_letter}: " in row_val or row_val == team.team_letter:
            rgb = team.rgb_colors
            return f"background-color: rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
    if row_val in ["AB", "BC", "AC"]:
        return f"background-color: rgba(255, 255, 50, {alpha})"
    return ""


def st_style_df_with_team_vals(
    df: pd.DataFrame, data: DataRegistry, full_row=False
) -> Styler:
    """Display a DataFrame with the team colors highlighted.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to display.
    full_row : bool, optional
        If True, the whole row will be colored, otherwise format each entry individually, by default False.
    """
    # We need to hide the index column, this only works if we convert to HTML
    style = df.style
    if full_row:
        style = style.apply(
            lambda row: [_get_row_color(row["full_key"])] * len(row), axis=1  # type: ignore
        )
    else:
        style = style.apply(
            lambda row: [_get_row_color(data, val) for val in row], axis=1
        )
    return style


def _get_val_color(val: str) -> str:
    if str(val) != "" and str(val) in "ABCDEF":
        return f"background-color: rgba(0, 0, 255, 0.5)"
    return "background-color: none"


def st_display_single_team_table(df: pd.DataFrame, container=None):
    """Display a DataFrame with the team colors highlighted.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to display.
    """
    # We need to hide the index column, this only works if we convert to HTML
    style = df.style
    style = style.apply(lambda row: [_get_val_color(val) for val in row], axis=1)
    style.hide()
    if container is not None:
        container.write(style.to_html(), unsafe_allow_html=True)
        return
    st.write(style.to_html(), unsafe_allow_html=True)


def generate_sports_page_files():
    for sport in SPORTS_LIST:
        ftext = f"""
'''This file is auto-generated. Do not edit it manually.
Re-Generate them via the 'generate_sports_page_files' function in 'streamlit_util.py'.
'''
import helper_functions as hf

hf.st_set_up_header_and_sidebar()
hf.SPORTS_EVENTS["{sport}"].write_streamlit_rep()
    """
        fpath = PAGESPATH.joinpath(f"events/{sport}.py")
        with fpath.open("w") as f:
            f.write(ftext.format(sport=sport))


def st_display_venn_sport_selection(data: DataRegistry) -> list[str]:
    all_sports = {
        (e := data.sport_events[sport]).icon + e.name: sport
        for sport in data.avail_sports
    }
    options = list(all_sports) + ["None"]

    cols = st.columns(5)
    for i, default_index in enumerate([0, 3, 6, len(options) - 1, len(options) - 1]):
        cols[i].selectbox(
            f"Axis {i + 1}",
            options=options,
            index=default_index,
            key=f"selectbox_{i}",
        )

    selected = np.unique([st.session_state[f"selectbox_{i}"] for i in range(5)])
    selected = [sport for sport in selected if sport != "None"]
    return [all_sports[sport] for sport in selected]
