import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.axes import Axes

from ...data_registry import DataRegistry


def _plot_cumulative_signups(
    data: pd.Series, label: str, min_time: pd.Timestamp, max_time: pd.Timestamp
):
    """Plot the data in a cumulative fashion, assuming that they are dates."""
    data = pd.to_datetime(data).apply(lambda x: min(x, max_time))
    data = pd.concat([data, pd.Series(min_time), pd.Series(max_time)]).sort_values()
    cumulative_signups = list(range(0, len(data)))
    # The last entry is the max time, so we don't want to count it as a sign-up:
    cumulative_signups[-1] -= 1
    (line,) = plt.plot(
        data,
        cumulative_signups,
        marker="none",
        label=label,
        lw=3,
        alpha=0.8,
        drawstyle="steps-post",
    )
    plt.axhline(
        y=len(data) - 2, color=line.get_color(), linestyle="--", lw=1, alpha=0.7
    )


def _setup_signup_plot():
    plt.xlabel("Time")
    plt.ylabel("Cumulative Sign-Ups")
    # plt.grid()
    plt.xticks(rotation=60)
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m."))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=60, ha="right")
    plt.legend(fontsize=10, bbox_to_anchor=(0.1, 0.98), loc="upper left")


def _annotate_time(ax: Axes, time: str, label: str = ""):
    annotation_time = pd.to_datetime(time)
    ax.axvline(annotation_time, color="red", linestyle="--")  # type: ignore
    ax.text(annotation_time, max(ax.get_ylim()) * 0.8, label, rotation=270, ha="left", va="center")  # type: ignore


def _annotate_timestamps():
    _annotate_time(plt.gca(), "2025-03-07 21:00:00", "Initial Mail")
    _annotate_time(plt.gca(), "2025-03-26 15:00:00", "MPQ-mail sent")
    _annotate_time(plt.gca(), "2025-03-28 10:00:00", "Reminder")


@st.fragment
def st_display_signup_times(data: DataRegistry):
    plot_type = st.radio(
        "Which sign-ups to plot", ["All", "Separated by institute"], horizontal=True
    )

    df = data.players
    min_time = pd.to_datetime(df["response_timestamp"]).min()
    max_time = pd.to_datetime("2025-04-04 23:59:59")
    fig, ax = plt.subplots(figsize=(5, 4))
    if plot_type == "All":
        ax.set_title("Cumulative Sign-Ups Over Time (All)")
        _plot_cumulative_signups(df["response_timestamp"], "Total", min_time, max_time)
        # _plot_cumulative_signups(df[df["has_paid_fee"]]["response_timestamp"], "Fee paid")
    else:
        ax.set_title("Cumulative Sign-Ups Over Time (By Institutes)")
        for institute in df["institute"].unique():
            subdf = df[df["institute"] == institute]
            _plot_cumulative_signups(
                subdf["response_timestamp"], institute, min_time, max_time
            )
    _setup_signup_plot()
    _annotate_timestamps()

    st.pyplot(fig)
