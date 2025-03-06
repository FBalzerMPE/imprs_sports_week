import streamlit as st

import helper_functions as hf

st.write("# Contact")

with st.expander("Why contact us?"):
    st.write(
        r"""
    Do you have any feedback you want to provide us with?\
    Do you have rules questions concerning a specific sport?\
    Are you not available for an event you've been scheduled?\
    Let us know via Email or Signal, you can find the people responsible for the events here.
    All members of the organizing committee are marked with a \* and listed first.\
    All members that you can approach to pay the 2 € sign-up fee are marked with a 💸.

    Big shoutout to all the amazing people helping out with the organization of the sports week! 🎉
    """
    )
with st.expander("Note on email addresses"):
    st.write(
        r"""For spam prevention, the email addresses do not contain the domain beyond the "@" symbol.
The correct address endings are as follows:

- @1... $\rightarrow$ mpe.mpg.de
- @2... $\rightarrow$ mpa-garching.mpg.de
- @3... $\rightarrow$ ipp.mpg.de
- @4... $\rightarrow$ mpp.mpg.de
- @5... $\rightarrow$ mpq.mpg.de
- @6... $\rightarrow$ campus.lmu.de
- @7... $\rightarrow$ eso.org
""",
    )


hf.st_display_organizers(hf.DATA_NOW, True)
