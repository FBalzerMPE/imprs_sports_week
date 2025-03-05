# Inter-institute Sports Week Garching 2024

Presenting the web page for all information concerning the inter-institute sports weeks held in Garching.

This repo also contains a few tools to analyze the survey results, to compose teams and subteams, and to schedule matches.

Allows to create some plots and somewhat balanced teams based on a random way
of finding them that is good enough for our purposes, albeit I admit it isn't really optimized.

Most stuff can be found in `analyze_sportsweek_data.ipynb` for now, might change later.

The structure is a little weird due to the requirements of streamlit, but on top level, there are a few notebooks for the tasks to set up the initial data (and schedule).

The important stuff is hosted in the `helper_functions` module, while the `streamlit_app.py` script and the `pages` directory contain all python files used to run the webpage.
