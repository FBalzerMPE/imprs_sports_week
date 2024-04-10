import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator

from .constants import SPORTS_LIST
from .data_registry import ALL_TEAMS
from .plot_util import annotate_barh_values, plot_pie_chart
from .sport_event_registry import SPORTS_EVENTS
from .util import sort_dict_by_values


def create_institute_plot(df: pd.DataFrame):
    ax = plt.gca()
    plot_pie_chart(
        df["is_postdoc"].tolist(),
        ax,
        radius=0.6,
        width=0.2,
        colors=["gold", "darkred"],
        add_text=False,
        pctdistance=0.8,
    )

    return plot_pie_chart(
        df["institute"].tolist(),
        ax,
        "Institute\ndistribution",
        is_institute_chart=True,
        width=0.3,
    )


def create_sports_num_plot(
    df: pd.DataFrame,
    annotate_numbers=True,
    sort_bars=False,
    color: str | tuple = "gold",
    y_offset: float = 0,
    **kwargs,
):
    sport_totals: dict[str, int] = {flag: df[flag].sum() for flag in SPORTS_LIST}
    if sort_bars:
        sport_totals = sort_dict_by_values(sport_totals)
    values = list(sport_totals.values())
    y_positions = [i + y_offset for i in range(len(SPORTS_LIST))]
    ax: Axes = plt.gca()
    containers = ax.barh(
        y_positions, values, color=color, edgecolor="black", linewidth=1, **kwargs  # type: ignore
    )

    plt.yticks(range(len(sport_totals)), list(sport_totals.keys()))
    ax.set_xlabel("Number of people interested")
    ax.set_title(f"Willingness to participate in sports ({len(df)} total responses)")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, axis="x")
    if annotate_numbers:
        annotate_barh_values(ax, containers, x_displacement=0.5)


def _prepare_institute_data() -> pd.DataFrame:
    all_players = pd.concat([team.player_df for team in ALL_TEAMS])
    # Count the number of players from each institute, divided by teams
    institute_data = all_players.groupby(["institute", "Team"]).size().reset_index(name="Count").sort_values("Team")  # type: ignore
    institute_data["Short_Team"] = institute_data["Team"].str.replace("Team ", "")
    return institute_data


def _prepare_postdoc_data() -> pd.DataFrame:
    all_players = pd.concat([team.player_df for team in ALL_TEAMS])
    # Count the number of postdocs, divided by teams
    postdoc_data = all_players.groupby(["is_postdoc", "Team"]).size().reset_index(name="Count").sort_values("Team")  # type: ignore
    postdoc_data["is_postdoc"] = postdoc_data["is_postdoc"].map(
        {True: "PostDoc", False: "PhD"}
    )
    return postdoc_data


def _prepare_sports_data() -> pd.DataFrame:

    datasets = []
    for team in ALL_TEAMS:
        df = team.player_df
        sport_totals: dict[str, int] = {
            event.icon + event.name: df[flag].sum()
            for flag, event in SPORTS_EVENTS.items()
        }

        data = pd.DataFrame(list(sport_totals.items()), columns=["Sport", "Total"])
        data["Team"] = team.name
        data["Color"] = team.color
        datasets.append(data)

    return pd.concat(datasets)


def create_sport_dist_altair_chart() -> alt.Chart:

    click_team = alt.selection_point(fields=["Team"])
    team_colors = alt.Color(
        "Team:N", scale=alt.Scale(range=[team.color for team in ALL_TEAMS])
    )

    # Create main bar chart
    bar_chart = (
        alt.Chart(_prepare_sports_data())
        .mark_bar(height=7)
        .encode(
            x=alt.X("Total", title="People interested in sport"),
            yOffset="Team",
            y=alt.Y("Sport:N", sort="-x"),
            color=alt.condition(click_team, team_colors, alt.value("lightgray")),  # type: ignore
            opacity=alt.value(0.5),
        )
        .properties(height=300)
        .add_params(click_team)
    )

    # - Create pie chart of institutes:
    pie_chart = (
        alt.Chart(_prepare_institute_data())
        .mark_arc(outerRadius=89, innerRadius=50, stroke="black", strokeWidth=1)
        .encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("institute:N", scale=alt.Scale(scheme="category20")),
            tooltip=alt.Tooltip("Count:Q"),
            order={"field": "institute", "sort": "ascending", "type": "quantitative"},
        )
        .transform_filter(click_team)
        .properties(height=200, width=200, title="Institute distribution")
    )
    # Add text labels to the pie chart
    text = pie_chart.mark_text(
        radius=97,
        align="center",
        baseline="middle",
        dx=0,  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(text="Short_Team:N", theta=alt.Theta("Count:Q", stack=True))
    pie_chart = pie_chart + text
    # - Postdoc_chart
    postdoc_chart = (
        alt.Chart(_prepare_postdoc_data())
        .mark_bar()
        .encode(
            x=alt.X("is_postdoc:N", title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Count:Q", title="Count"),
            color=team_colors,
            opacity=alt.value(0.7),
        )
        .transform_filter(click_team)
        .properties(height=200, title="PhD/Postdoc distinction")
    )

    # - Put everything together
    bottom_chart = alt.hconcat(postdoc_chart, pie_chart).resolve_scale(
        color="independent"
    )

    chart = alt.vconcat(
        bar_chart,
        bottom_chart,
        title="Distribution of sports amongst the teams",
    ).resolve_scale(color="independent")

    return chart  # type: ignore
