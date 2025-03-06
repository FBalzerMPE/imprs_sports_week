import streamlit as st
from typing import Callable
from ..data_registry import DataRegistry


def st_display_organizers(
    data: DataRegistry,
    add_pic_toggle: bool = False,
    filter_func: Callable | None = None,
):
    """Display the organizers in the Streamlit app.

    Parameters
    ----------
    data : DataRegistry
        The data registry object.
    add_pic_toggle : bool, optional
        Whether to add a toggle for showing pictures, by default False
    filter_func : Callable, optional
        A function to filter the organizers, by default None
    """
    if add_pic_toggle:
        cols = st.columns(2)
        show_pics = (
            cols[0].checkbox(
                "Show pictures",
                value=True,
                # ["Yes", "No"],
                # horizontal=True,
                help="Whether to show organizer pics (might want to hide them on mobile).",
            )
            # == "Yes"
        )
        expand_all = (
            cols[1].checkbox(
                "Expand all",
                value=False,
                # ["No", "Yes"],
                # horizontal=True,
                help="Whether to use expanders for each organizer.",
            )
            # == "Yes"
        )
    else:
        show_pics = True
        expand_all = False
    col1, col2 = st.columns(2)

    organizers = (
        filter_func(data.organizers.values())
        if filter_func is not None
        else data.organizers.values()
    )

    for i, sports_organizer in enumerate(organizers):
        if i % 2 == 0:
            with col1:
                sports_organizer.st_display_info(
                    show_pics, use_expander=add_pic_toggle and not expand_all
                )
        else:
            with col2:
                sports_organizer.st_display_info(
                    show_pics, use_expander=add_pic_toggle and not expand_all
                )
