import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from venn import venn

from ...classes.team import Team
from ...constants import SPORTS_LIST
from ...data_registry import DataRegistry
from ...util import sort_dict_by_values
from .plot_util import annotate_barh_values


def _prepare_institute_data(teams: list[Team]) -> pd.DataFrame:
    all_players = pd.concat([team.player_df for team in teams])
    # Count the number of players from each institute, divided by teams
    institute_data = all_players.groupby(["institute", "Team"]).size().reset_index(name="Count").sort_values("Team")  # type: ignore
    institute_data["Short_Team"] = institute_data["Team"].str.replace("Team ", "")
    return institute_data


def _prepare_postdoc_data(teams: list[Team]) -> pd.DataFrame:
    all_players = pd.concat([team.player_df for team in teams])
    # Count the number of postdocs, divided by teams
    postdoc_data = all_players.groupby(["is_postdoc", "Team"]).size().reset_index(name="Count").sort_values("Team")  # type: ignore
    postdoc_data["is_postdoc"] = postdoc_data["is_postdoc"].map(
        {True: "PostDoc", False: "PhD"}
    )
    return postdoc_data


def _prepare_sports_data(data: DataRegistry) -> pd.DataFrame:

    datasets = []
    for team in data.teams:
        df = team.player_df
        sport_totals: dict[str, int] = {
            event.icon + event.name: df[flag].sum()
            for flag, event in data.sport_events.items()
            if flag in df.columns
        }

        df2 = pd.DataFrame(list(sport_totals.items()), columns=["Sport", "Total"])
        df2["Team"] = team.name
        df2["Color"] = team.color
        datasets.append(df2)

    return pd.concat(datasets)


def _get_team_colors(teams: list[Team]) -> alt.Color:
    return alt.Color("Team:N", scale=alt.Scale(range=[team.color for team in teams]))


def get_team_distribution_chart(data: DataRegistry) -> alt.Chart:
    bar_chart = (
        alt.Chart(_prepare_sports_data(data))
        .mark_bar(height=7)
        .encode(
            x=alt.X("Total", title="People interested in sport"),
            yOffset="Team",
            y=alt.Y("Sport:N", sort="-x"),
            color=_get_team_colors(data.teams),
            opacity=alt.value(0.5),
        )
        .properties(height=300)
    )
    return bar_chart


def get_institute_distribution_chart(data: DataRegistry) -> alt.Chart | alt.LayerChart:
    pie_chart = (
        alt.Chart(_prepare_institute_data(data.teams))
        .mark_arc(outerRadius=89, innerRadius=50, stroke="black", strokeWidth=1)
        .encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("institute:N", scale=alt.Scale(scheme="category20")),
            tooltip=alt.Tooltip("Count:Q"),
            order={"field": "institute", "sort": "ascending", "type": "quantitative"},
        )
        .properties(height=200, width=200, title="Institute distribution")
    )
    text = pie_chart.mark_text(
        radius=97,
        align="center",
        baseline="middle",
        dx=0,
    ).encode(text="Short_Team:N", theta=alt.Theta("Count:Q", stack=True))
    pie_chart = pie_chart + text
    return pie_chart


def get_postdoc_distribution_chart(data: DataRegistry) -> alt.Chart:
    postdoc_chart = (
        alt.Chart(_prepare_postdoc_data(data.teams))
        .mark_bar()
        .encode(
            x=alt.X("is_postdoc:N", title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Count:Q", title="Count"),
            color=_get_team_colors(data.teams),
            opacity=alt.value(0.7),
        )
        .properties(height=200, title="PhD/Postdoc distinction")
    )
    return postdoc_chart


def st_display_player_overview(data: DataRegistry):
    c = get_team_distribution_chart(data)
    st.altair_chart(c, theme="streamlit", use_container_width=True)
    c2 = get_institute_distribution_chart(data)
    c3 = get_postdoc_distribution_chart(data)
    comb = alt.hconcat(c2, c3).resolve_scale(color="independent")
    st.altair_chart(comb, theme="streamlit", use_container_width=True)


# def create_sport_dist_altair_chart(data: DataRegistry) -> alt.Chart | alt.VConcatChart:

#     team_colors = alt.Color(
#         "Team:N", scale=alt.Scale(range=[team.color for team in data.teams])
#     )

#     # - Create main bar chart
#     bar_chart = (
#         alt.Chart(_prepare_sports_data(data))
#         .mark_bar(height=7)
#         .encode(
#             x=alt.X("Total", title="People interested in sport"),
#             yOffset="Team",
#             y=alt.Y("Sport:N", sort="-x"),
#             color=team_colors,
#             # color=alt.condition(click_team, team_colors, alt.value("lightgray")),  # type: ignore
#             opacity=alt.value(0.5),
#         )
#         .properties(height=300)
#         # .add_params(click_team)
#     )

#     # - Create pie chart of institutes:
#     pie_chart = (
#         alt.Chart(_prepare_institute_data(data.teams))
#         .mark_arc(outerRadius=89, innerRadius=50, stroke="black", strokeWidth=1)
#         .encode(
#             theta=alt.Theta("Count:Q"),
#             color=alt.Color("institute:N", scale=alt.Scale(scheme="category20")),
#             tooltip=alt.Tooltip("Count:Q"),
#             order={"field": "institute", "sort": "ascending", "type": "quantitative"},
#         )
#         # .transform_filter(click_team)
#         .properties(height=200, width=200, title="Institute distribution")
#     )
#     # Add text labels to the pie chart
#     text = pie_chart.mark_text(
#         radius=97,
#         align="center",
#         baseline="middle",
#         dx=0,  # Nudges text to right so it doesn't appear on top of the bar
#     ).encode(text="Short_Team:N", theta=alt.Theta("Count:Q", stack=True))
#     pie_chart = pie_chart + text
#     # - Postdoc_chart
#     postdoc_chart = (
#         alt.Chart(_prepare_postdoc_data(data.teams))
#         .mark_bar()
#         .encode(
#             x=alt.X("is_postdoc:N", title="", axis=alt.Axis(labelAngle=-45)),
#             y=alt.Y("Count:Q", title="Count"),
#             color=team_colors,
#             opacity=alt.value(0.7),
#         )
#         # .transform_filter(click_team)
#         .properties(height=200, title="PhD/Postdoc distinction")
#     )

#     # - Put everything together
#     bottom_chart = alt.hconcat(postdoc_chart, pie_chart).resolve_scale(
#         color="independent"
#     )

#     chart = alt.vconcat(
#         bar_chart,
#         bottom_chart,
#         title="Distribution of sports amongst the teams",
#     ).resolve_scale(color="independent")

#     return bar_chart
