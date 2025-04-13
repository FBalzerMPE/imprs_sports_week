from typing import Optional

import numpy as np
import streamlit as st
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from matplotlib.lines import Line2D

from ...util import sort_dict_by_values


def annotate_barh_values(
    ax: Axes,
    containers: BarContainer,
    x_displacement: float = 0,
    bbox: Optional[dict] = None,
    formatter="{}",
    **kwargs,
):
    """Annotate the values on an ax where the containers come from a given hbar diagram

    Parameters
    ----------
    ax : Axes
        The axes to annotate the values on
    containers : list[any]
        The containers from the bar plot
    x_displacement : float, optional
        The amount of horizontal distance the values should be displaced by, by default 0
    bbox : dict, optional
        The dictionary describing the bbox for the background of the annotations,
        by default dict(facecolor="white", boxstyle="round,pad=0.1")
    formatter : str, optional
        The formatter used for the numbers, by default "{}"
    """
    bbox = dict(facecolor="white", boxstyle="round,pad=0.1") if bbox is None else bbox
    for rec in containers:  # Annotate the amount in each bin.
        x = rec.get_width() + x_displacement
        y = rec.get_y() + rec.get_height() / 2
        text = formatter.format(rec.get_width())
        ax.text(x, y, text, verticalalignment="center", bbox=bbox, **kwargs)


def plot_pie_chart(
    data: list[str],
    ax: Axes,
    title: str = "",
    is_institute_chart=False,
    add_text=True,
    legend_title: str | None = None,
    **kwargs,
):
    num_dict = {
        class_: count for class_, count in zip(*np.unique(data, return_counts=True))  # type: ignore
    }
    num_dict = sort_dict_by_values(num_dict)
    colors = kwargs.get("colors", ["none"])
    if is_institute_chart:
        institutes = sorted(np.unique(data))
        colors = [cm.tab10.colors[i] for i, inst in enumerate(institutes)]  # type: ignore

    labels = (
        [f"{class_} ({count})" for class_, count in num_dict.items()]
        if add_text
        else None
    )
    title = f"{title}\n({len(data)})" if title != "" else f"{len(data)} points"
    ax.axis("equal")
    radius = kwargs.get("radius", 0.9)
    width = kwargs.get("width", 0.4)
    pctdistance = kwargs.get("pctdistance", radius - 0.1)
    lw = kwargs.get("lw", 2)
    ax.pie(
        list(num_dict.values()),
        startangle=0,
        radius=radius,
        labels=labels,
        labeldistance=1.06,
        textprops={
            "size": "smaller",
            "bbox": dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                edgecolor="black",
                alpha=0.9,
            ),
        },
        autopct="%.0f%%",
        pctdistance=pctdistance,
        wedgeprops=dict(width=width, linewidth=lw, ec="k"),
        colors=colors,
    )
    if add_text:
        # Add title in the centre
        ax.text(0, 0, title, ha="center", va="center", fontsize="small")
    if legend_title is not None:
        # Pie chart doesn't add those automatically, so we add them manually:
        handles = [
            Line2D([0], [0], marker="o", color="k", label=label, linestyle="none", markerfacecolor=color, markersize=10)  # type: ignore
            for label, color in zip(num_dict.keys(), colors)
        ]
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(0.8, 1),
            fontsize="small",
            title=legend_title,
            title_fontsize="small",
            handles=reversed(handles),
            labels=reversed(num_dict.keys()),
        )
