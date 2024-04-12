from typing import Literal

import pandas as pd
import pydeck as pdk
import streamlit as st

from .util import turn_series_list_to_dataframe

MAP_OPTIONS = ["streets", "satellite", "outdoors"]


def create_map_plot(highlighted_locations: list[str]):
    """Create a map plot with highlighted locations."""
    from .sport_event_registry import ALL_LOCATIONS

    df = turn_series_list_to_dataframe(
        [loc.as_series for loc in ALL_LOCATIONS.values()]
    )

    highlight_df = df[df["name"].isin(highlighted_locations)]

    # Define a tooltip for the layers
    tooltip = {
        "html": "<b>{desc}</b>",  # Display the description of the location in the tooltip
        "style": {
            "backgroundColor": "black",
            "color": "white",
            "padding": "12px",
            "border": "1px",
            "border-radius": "5px",
            "width": "200px",
        },
    }
    mpe_entrance = (48.261778, 11.671638, "MPE Entrance", "Entrance to MPE")
    mpa_entrance = (48.260992, 11.671281, "MPA Entrance", "Entrance to MPA")

    extra_df = pd.DataFrame(
        [mpe_entrance, mpa_entrance],
        columns=["latitude", "longitude", "display_name", "desc"],
    )

    LAYERS = {
        "All locations": pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_color=[0, 100, 0, 160],
            get_radius=20,
            radius_scale=0.1,
        ),
        "Highlighted locations": pdk.Layer(
            "ScatterplotLayer",
            data=highlight_df,
            get_position=["longitude", "latitude"],
            get_color=[200, 0, 0, 200],
            get_radius=40,
            radius_scale=0.1,
        ),
        "Extra locations": pdk.Layer(
            "ScatterplotLayer",
            data=extra_df,
            get_position=["longitude", "latitude"],
            get_color=[0, 0, 200, 200],
            get_radius=15,
            radius_scale=0.1,
        ),
        "Annotations": pdk.Layer(
            "TextLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_text="display_name",
            get_color=[0, 0, 0, 255],
            get_size=15,
            get_alignment_baseline="'bottom'",
            get_font_family="'Courier New'",  # Set the font of the text
            get_font_weight=700,  # Set the font weight of the text
            pickable=True,  # Make the layer clickable
            auto_highlight=True,  # Highlight the layer when it's clicked
            tooltip=tooltip,  # Use the tooltip
        ),
        "Extra annotations": pdk.Layer(
            "TextLayer",
            data=extra_df,
            get_position=["longitude", "latitude"],
            get_text="display_name",
            get_color=[0, 0, 0, 200],
            get_size=13,
            get_alignment_baseline="'bottom'",
            pickable=True,  # Make the layer clickable
            # auto_highlight=True,  # Highlight the layer when it's clicked
            tooltip=tooltip,  # Use the tooltip
        ),
    }

    style = st.radio("Map style", MAP_OPTIONS, horizontal=True)
    if style is None:
        style = "streets"
    st.pydeck_chart(
        pdk.Deck(
            map_style=f"mapbox://styles/mapbox/{style}-v9",
            initial_view_state=pdk.ViewState(
                latitude=48.261925,
                longitude=11.673458,
                zoom=15,
                min_zoom=10,
                max_zoom=20,
            ),
            layers=list(LAYERS.values()),
            tooltip=tooltip,  # type: ignore
        )
    )
