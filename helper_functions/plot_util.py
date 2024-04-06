from typing import Optional

import numpy as np
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.container import BarContainer

from .util import sort_dict_by_values


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
    data: list[str], ax: Axes, title: str = "", is_institute_chart=False
):
    num_dict = {
        class_: count for class_, count in zip(*np.unique(data, return_counts=True))
    }
    num_dict = sort_dict_by_values(num_dict)
    colors = "none"
    if is_institute_chart:
        inst_dict = {"MPE": 0, "MPA": 1, "USM": 2, "ESO": 3, "IPP": 4}
        colors = [cm.tab10.colors[inst_dict[key]] for key in num_dict]  # type: ignore

    labels = [f"{class_} ({count})" for class_, count in num_dict.items()]
    title = f"{title}\n({len(data)})" if title != "" else f"{len(data)} points"
    ax.axis("equal")
    ax.pie(
        list(num_dict.values()),
        startangle=90,
        radius=0.9,
        labels=labels,
        labeldistance=1.04,
        textprops={"size": "smaller"},
        autopct="%.0f%%",
        pctdistance=0.8,
        wedgeprops=dict(width=0.4, ec="k"),
        colors=colors,
    )
    # Add title in the centre
    ax.text(0, 0, title, ha="center", va="center", fontsize="small")
