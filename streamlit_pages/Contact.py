import streamlit as st

import helper_functions as hf

st.write("# Contact")

st.write(
    r"""
Do you have any feedback you want to provide us with?\
Do you have rules questions concerning a specific sport?\
Are you not available for an event you've been scheduled?\
Let us know via Email or Signal, you can find the people responsible for the events here. All members of the organizing committee are marked with a \*.

For spam prevention, the email addresses do not contain the domain beyond the "@" symbol.
The correct address endings are as follows:

- @1... $\rightarrow$ mpe.mpg.de
- @2... $\rightarrow$ mpa-garching.mpg.de
- @3... $\rightarrow$ ipp.mpg.de
- @4... $\rightarrow$ mpp.mpg.de
""",
)


hf.st_display_organizers(hf.DATA_NOW, True)
