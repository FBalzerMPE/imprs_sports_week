import numpy as np
import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from venn import venn

from ...data_registry import DataRegistry


def st_display_overlap_of_sports(sports_list: list[str], data: DataRegistry):
    if len(sports_list) <= 1:
        st.warning("Please select at least two different sports.")
        return
    # Let the user create a venn diagram of the three sports:
    df = data.players[sports_list].copy()
    venn_data = {
        f"{data.sport_events[key].name} ({np.sum(df[key])})": set(df.index[df[key]])
        for key in sports_list
    }

    ax: Axes = venn(venn_data, cmap="tab10", alpha=0.6)
    for patch in ax.patches:
        if patch:  # Check if the patch exists
            patch.set_edgecolor("black")  # Add a border
    fig: Figure = ax.get_figure()  # type: ignore
    fig.set_facecolor("none")
    fig.set_size_inches(8, 8)
    fig.suptitle(
        "Overlap of selected sports",
        font_properties={"weight": "bold", "size": 20},
        bbox={
            "facecolor": "white",
            "edgecolor": "black",
            "boxstyle": "round,pad=0.3",
        },
        y=0.95,
    )
    st.pyplot(fig)
