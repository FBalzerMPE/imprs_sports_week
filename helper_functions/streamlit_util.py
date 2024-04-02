import pandas as pd
import streamlit as st


def _get_row_color(row_val: str, alpha: float = 0.3) -> str:
    from .team_registry import ALL_TEAMS

    for team in ALL_TEAMS:
        if str(team.team_index) in row_val and " " in row_val:
            rgb = team.rgb_colors
            return f"background-color: rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
    return "background-color: none"


def st_disply_team_highlighted_table(df: pd.DataFrame, full_row=False):
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
            lambda row: [_get_row_color(row["Team"])] * len(row), axis=1
        )
    else:
        style = style.apply(lambda row: [_get_row_color(val) for val in row], axis=1)
    style.hide()
    st.write(style.to_html(), unsafe_allow_html=True)
