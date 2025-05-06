import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from ..constants import DATAPATH, FpathRegistry
from ..data_registry import DataRegistry
from .streamlit_util import st_style_df_with_team_vals

_POINT_EXPLANATION = """
The points are calculated by taking the total amount of points achieved for each team, weighted by the number of players that participated in the sub-event, and are then brought back to the total amount of points achieved (30 for Sprints, 35 for Endurance, 35 for the relay)."""


def calculate_points(df: pd.DataFrame) -> dict[str, float]:
    """Calculate the points for each team."""
    total_amount = np.sum(df["points"])
    weights = np.array([np.sum(df["Team"] == team) for team in "ABC"]) / len(df)
    initial_points = np.array([sum(df[df["Team"] == team]["points"]) for team in "ABC"])
    final_points = initial_points / weights
    # Bring them back up to the initial total amount of points
    final_points = final_points / np.sum(final_points) * total_amount
    return {team: round(points) for team, points in zip("ABC", final_points)}


def display_sprints_df(df: pd.DataFrame, data: DataRegistry):
    """Style the match dataframe and display it properly."""
    df["Place"] = df["time"].rank(method="min").astype(int)
    df["avatar"] = df["nickname"].apply(lambda x: FpathRegistry.get_animal_pic_path(x))
    df = df.sort_values("Place")
    column_configs = {}
    column_configs["time"] = st.column_config.Column("Time", width="small")
    column_configs["Place"] = st.column_config.Column("Place", width="small")
    column_configs["nickname"] = st.column_config.TextColumn("Nickname")
    column_configs["points"] = st.column_config.TextColumn("Points", width="small")
    column_configs["avatar"] = st.column_config.ImageColumn("Avatar", width="small")

    style = st_style_df_with_team_vals(df, data)
    st.dataframe(
        style,
        hide_index=True,
        column_config=column_configs,
        column_order=["Place", "Team", "avatar", "nickname", "time", "points"],
    )


@st.cache_data(ttl=60 * 60 * 24)
def load_running_df(fname: str, data: DataRegistry) -> pd.DataFrame:
    """Load the sprints dataframe."""
    fpath = DATAPATH.joinpath(f"2025/running_sprints_results/{fname}")
    df = pd.read_csv(fpath).set_index("nickname", drop=False)
    df = df.join(data.players.set_index("nickname")[["Team"]])
    df["Team"] = df["Team"].str.replace("Team ", "")
    return df


def display_endurance_results(data: DataRegistry):
    """Display the endurance results."""
    st.title("Endurance Results")
    st.write("This is the result of the endurance event.")
    df = load_running_df("endurance.csv", data)
    display_sprints_df(df, data)
    points = calculate_points(df)
    st.write("This resulted in the following points:")
    st.write("\n".join([f"{t}: {p}" for t, p in points.items()]))


def display_sprints_results(data: DataRegistry):
    """Display the sprints results."""
    st.title("Sprints Results")
    st.write("This is the result of the sprints event.")
    df = load_running_df("sprints.csv", data)
    tabs = st.tabs([f"Leg {i}" for i in range(1, 6)])
    for i, tab in enumerate(tabs):
        subdf = df[df["leg"] == i + 1]
        with tab:
            display_sprints_df(subdf, data)
    st.write("This resulted in the following points:")
    points = calculate_points(df)
    st.write("\n".join([f"{t}: {p}" for t, p in points.items()]))
    st.expander("Points Calculation", expanded=False).markdown(_POINT_EXPLANATION)


def _get_score_df(data: DataRegistry) -> pd.DataFrame:
    sprints = load_running_df("sprints.csv", data)
    sprints_points = calculate_points(sprints)
    endurance = load_running_df("endurance.csv", data)
    endurance_points = calculate_points(endurance)
    relay_points = {"A": 0, "B": 23, "C": 12}
    point_df = pd.DataFrame(
        {
            "Team": ["A", "B", "C"],
            "Sprints": [sprints_points[t] for t in "ABC"],
            "Relay": [relay_points[t] for t in "ABC"],
            "Endurance": [endurance_points[t] for t in "ABC"],
        }
    ).set_index("Team")
    return point_df


def display_points_plot(data: DataRegistry):
    score_df = _get_score_df(data)
    team_colors = alt.Color(
        "Team:N", scale=alt.Scale(range=[team.color for team in data.teams])
    )

    # Create the horizontal stacked bar plot
    chart = (
        alt.Chart(score_df)
        .mark_bar()
        .encode(
            y=alt.Y("Sport:N", title="", axis=alt.Axis(labelFontWeight="bold")),
            x=alt.X("Score:Q"),
            color=team_colors,
            order=alt.Order(
                # Sort the segments of the bars by this field
                "Team:N",
            ),
            opacity=alt.value(0.5),
        )
        .properties(title="Score distribution")
    )

    st.altair_chart(chart, theme="streamlit", use_container_width=True)
