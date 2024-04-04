import helper_functions as hf
import matplotlib.pyplot as plt
import streamlit as st

hf.st_set_up_header_and_sidebar()


fig, ax = plt.subplots()
for team in hf.ALL_TEAMS:
    team.plot_sports_num()
ax.set_title("Number of players per team")
ax.legend()

st.pyplot(fig)
