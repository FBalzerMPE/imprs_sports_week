from datetime import datetime

import streamlit as st

import helper_functions as hf
from helper_functions.classes.player import Player

_timestamp = hf.FpathRegistry.get_path_responses().stat().st_mtime
last_date = datetime.fromtimestamp(_timestamp).strftime("%Y-%m-%d, %H:%M")

st.write(
    f"""## Participants (Status: {last_date})
        
For now, you can find some cryptic information on all {len(hf.DATA_NOW.players)} participants that have signed up so far.\\
Keep in mind that we might not update this super often, so it might take a bit until you're listed here. Also, of course you might not know about yourself even being listed here as the nicknames are quite anonymous, but oh well ;).

:warning: Note that it might take some time for your payment info to seep through, so especially that information might not be up to date. 💸💸💸
         """
)

tabs = st.tabs(["Detailed", "Data"])
with tabs[0]:
    cols = st.columns(2)
    show_avatars = (
        cols[0].checkbox(
            "Show avatar pics",
            value=True,
            # ["Yes", "No"],
            # horizontal=True,
            help="Whether to show avatars (might want to hide them on mobile).",
        )
        # == "Yes"
    )
    show_inst_pics = (
        cols[1].checkbox(
            "Show institutes",
            value=False,
            # ["Yes", "No"],
            # horizontal=True,
            help="Whether to show pics of the institutes.",
        )
        # == "Yes"
    )
    insts = [p.stem for p in hf.DATAPATH.joinpath("assets/institute_logos").iterdir()]
    allowed_insts = st.multiselect(
        "Institute filter",
        insts,
        default=insts,
        help="Filter the candidates for institutes.",
    )

    cols = st.columns(2)

    filtered_players = hf.DATA_NOW.players
    filtered_players = filtered_players[
        filtered_players["institute"].apply(
            lambda x: x.lower().replace("/lmu", "") in allowed_insts
        )
    ]
    filtered_players.sort_values("nickname", inplace=True)
    for i, player in filtered_players.iterrows():
        with cols[i % 2]:  # type: ignore
            p = Player.from_series(player, [])
            p.write_streamlit_rep(
                info_only=True, show_avatars=show_avatars, show_inst=show_inst_pics
            )
with tabs[1]:
    # hf.st_style_df_with_team_vals(filtered_players, hf.DATA_NOW)
    st.write(":construction: Work in progress...")
    pass  # TODO: Implement this
