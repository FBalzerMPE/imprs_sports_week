import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from ..constants import DATAPATH, FpathRegistry
from ..data_registry import DataRegistry
from .streamlit_util import st_style_df_with_team_vals

_POINT_EXPLANATION = """
The points are calculated by taking the total amount of points achieved for each team, weighted by the number of players that participated in the sub-event, and are then brought back to the total amount of points achieved (30 for Sprints, 40 for Endurance, 30 for the relay)."""


def _add_weighted_points_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column with the weighted points for each row."""
    avg_pts = df["points"].sum()
    team_weights = df["Team"].value_counts(normalize=True).to_dict()
    df["weighted_points"] = df.apply(
        lambda row: row["points"] / team_weights[row["Team"]] / avg_pts * len(df),
        axis=1,
    )
    return df


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
    column_configs["weighted_points"] = st.column_config.TextColumn(
        "Points (weighted)", width="small"
    )

    style = st_style_df_with_team_vals(df, data)
    st.dataframe(
        style.format(subset=["weighted_points"], formatter="{:.1f}"),
        hide_index=True,
        column_config=column_configs,
        column_order=[
            "Place",
            "Team",
            "avatar",
            "nickname",
            "time",
            "points",
            "weighted_points",
        ],
    )


# @st.cache_data(ttl=60 * 60 * 24)
def load_running_df(fname: str, data: DataRegistry) -> pd.DataFrame:
    """Load the sprints dataframe."""
    fpath = DATAPATH.joinpath(f"2025/running_sprints_results/{fname}")
    df = pd.read_csv(fpath).set_index("nickname", drop=False)
    df = df.join(data.players.set_index("nickname")[["Team"]])
    df["Team"] = df["Team"].str.replace("Team ", "")
    df = _add_weighted_points_column(df)
    return df


def display_endurance_results(data: DataRegistry):
    """Display the endurance results."""
    with st.expander("Endurance Results", expanded=False):
        st.write(
            "In the endurance event, we had a race of approximately 3.3 km which was dominated by a certain Shady Turkey."
        )
        df = load_running_df("endurance.csv", data)
        display_sprints_df(df, data)
        points = calculate_points(df)
        st.write("The placements resulted in the following total points:")
        st.write("\n".join([f"{t}: {p}" for t, p in points.items()]))


def display_sprints_results(data: DataRegistry):
    """Display the sprints results."""
    with st.expander("Sprints Results", expanded=False):
        st.write(
            "In the sprint event, we 5 different legs of a sprinting distance around 80-90 m (times and distance might not be super accurate). In each leg, three people competed. The first place in each leg receives 4 points and second 2 points; For the final score, these are weighted by the number of players that participated in the sub-event for each main team (which is why the points achieved by Team C count less as there were many more participants)."
        )
        df = load_running_df("sprints.csv", data)
        tabs = st.tabs([f"Leg {i}" for i in range(1, 6)])
        for i, tab in enumerate(tabs):
            subdf = df[df["leg"] == i + 1].copy()
            with tab:
                display_sprints_df(subdf, data)
        st.write("The placements resulted in the following total points:")
        points = calculate_points(df)
        st.write("\n".join([f"{t}: {p}" for t, p in points.items()]))


def _get_score_df(data: DataRegistry) -> pd.DataFrame:
    sprints = load_running_df("sprints.csv", data)
    sprints_points = calculate_points(sprints)
    endurance = load_running_df("endurance.csv", data)
    endurance_points = calculate_points(endurance)
    relay_points = {"A": 0, "B": 20, "C": 10}
    point_df = pd.DataFrame(
        {
            "Team": ["A", "B", "C"],
            "Sprints": [sprints_points[t] for t in "ABC"],
            "Relay": [relay_points[t] for t in "ABC"],
            "Endurance": [endurance_points[t] for t in "ABC"],
        }
    )
    score_df = point_df.melt(id_vars="Team", var_name="Event", value_name="Score")

    total_scores = (
        score_df[score_df["Event"] != "Total Score"].groupby("Team")["Score"].sum()
    )
    for team, total_score in total_scores.items():
        new_row = pd.DataFrame(
            {
                "Team": [team],
                "Event": [f"Total Score {team}"],
                "Score": [total_score],
            }
        )
        score_df = pd.concat([score_df, new_row], ignore_index=True)
    return score_df


def display_running_sprints_points_plot(data: DataRegistry):
    score_df = _get_score_df(data)
    team_colors = alt.Color(
        "Team:N", scale=alt.Scale(range=[team.color for team in data.teams])
    )
    # Create the horizontal stacked bar plot
    chart = (
        alt.Chart(score_df)
        .mark_bar()
        .encode(
            y=alt.Y("Event:N", title="", axis=alt.Axis(labelFontWeight="bold")),
            x=alt.X("Score:Q"),
            color=team_colors,
            order=alt.Order(
                # Sort the segments of the bars by this field
                "Team:N",
            ),
            opacity=alt.value(0.5),
        )
        .properties(title="Score distribution for Running/Sprints")
    )
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


def display_relay_results():
    """Display the relay results."""
    with st.expander("Relay Results", expanded=False):
        st.write(
            "In the relay event, we had a 1.15 km relay with all players participating. The first place received 20 points and the second 10 points (and these are not rescaled)."
        )
        st.write("Here, Team B was the fastest, followed by Team C.")


def display_running_sprints_results(data: DataRegistry):
    """Display the running sprints results."""
    st.title("Running Sprints Results")
    st.write(
        "This is how the running/sprints event went this year - we had a bit of rain, but the participants withstood it magnificently, running as fast as they could in the following three events:"
    )
    display_sprints_results(data)
    display_endurance_results(data)
    display_relay_results()
    display_running_sprints_points_plot(data)
    st.expander("Points Calculation", expanded=False).markdown(_POINT_EXPLANATION)
