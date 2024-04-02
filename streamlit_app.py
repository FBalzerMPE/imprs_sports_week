import helper_functions as hf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from st_pages import Page, Section, add_indentation, add_page_title, show_pages

# Optional -- adds the title and icon to the current page
add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles
# and icons should be
show_pages(
    [
        Page("streamlit_app.py", "Home", "🏠"),
        Page("pages/schedule.py", "Schedule", ":calendar:"),
        Page("pages/teams.py", "Teams", ":family:"),
        Section(name="Sports", icon=":volleyball:"),
        Page("pages/events/volleyball.py", "Volleyball", ":volleyball:"),
        Page("pages/events/basketball.py", "Basketball", ":basketball:"),
        Section(name="Meet the organizers", icon=":smile:"),
    ]
)
add_indentation()
# sidebar.add_rows(["Home", "Teams", "Schedule", "Contact"])


# def main():
#     # Create a text element and let the reader know the data is loading.
#     data_load_state = st.text("Loading data...")
#     # Load 10,000 rows of data into the dataframe.
#     df = hf.sanitize_and_anonymize_data()
#     teams = hf.create_teams(df)

#     # Notify the reader that the data was successfully loaded.
#     data_load_state.text("")
#     st.subheader("Raw data")
#     st.write(df)
#     hf.create_institute_plot(df)
#     st.write(plt.gcf())

#     dates = pd.to_datetime(df["response_timestamp"]).dt.dayofyear
#     st.subheader("Number of registrations per day")
#     hist_values = np.histogram(dates, bins=dates.max() - dates.min())[0]
#     st.bar_chart(hist_values)


# if __name__ == "__main__":
#     main()
