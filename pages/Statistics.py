import helper_functions as hf
import streamlit as st

hf.st_set_up_header_and_sidebar()


st.write(
    """The following plots provide an overview of some attributes of the more than 90 participants of the sports week.
    
In the future, I may on providing a more detailed overview of how the teams were formed, and how the matches were scheduled.

Also, this is the site where you'll be able to see an overview of the results of the sports week, once it has started. Stay tuned!
"""
)
c = hf.create_sport_dist_altair_chart()
st.altair_chart(c, theme="streamlit", use_container_width=True)
