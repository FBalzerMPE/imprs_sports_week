import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from .plot_util import plot_pie_chart


def st_display_institute_dist_plot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("none")
    ax = plt.gca()
    plot_pie_chart(
        df["status"].tolist(),
        ax,
        radius=0.6,
        width=0.2,
        colors=list(["lightblue", "lightgreen", "darkred", "gold"]),
        add_text=False,
        pctdistance=0.8,
        legend_title="Status",
    )

    plot_pie_chart(
        df["institute"].tolist(),
        ax,
        "Institute and status\ndistribution",
        is_institute_chart=True,
        width=0.3,
    )
    st.pyplot(fig=plt.gcf(), clear_figure=True)
