import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator

from .constants import SPORTS_LIST
from .plot_util import annotate_barh_values, plot_pie_chart
from .util import sort_dict_by_values


def create_institute_plot(df: pd.DataFrame):
    ax = plt.gca()
    return plot_pie_chart(
        df["institute"].tolist(), ax, "Institute distribution", is_institute_chart=True
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
        y_positions, values, color=color, edgecolor="black", linewidth=1, **kwargs
    )

    plt.yticks(range(len(sport_totals)), list(sport_totals.keys()))
    ax.set_xlabel("Number of people interested")
    ax.set_title(f"Willingness to participate in sports ({len(df)} total responses)")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, axis="x")
    if annotate_numbers:
        annotate_barh_values(ax, containers, x_displacement=0.5)
