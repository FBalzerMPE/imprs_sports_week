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


tabs = st.tabs(["Compact", "Detailed", "Schedules"])
with tabs[1]:
    cols = st.columns(3)
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
        cols[0].checkbox(
            "Show institutes",
            value=False,
            # ["Yes", "No"],
            # horizontal=True,
            help="Whether to show pics of the institutes.",
        )
        # == "Yes"
    )
    sort_by = cols[1].selectbox(
        "Sort by",
        ["Nickname", "Institute", "Number of sports"],
        index=0,
        help="How to sort the players.",
    )
    reverse_sort = cols[2].checkbox(
        "Reverse sort",
        value=False,
        help="Whether to reverse the sort order.",
    )
    sort_by = "num_sports" if sort_by == "Number of sports" else sort_by.lower()
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
    filtered_players = filtered_players.sort_values(
        sort_by.lower(), ascending=not reverse_sort
    )
    for i, player in filtered_players.iterrows():
        with cols[i % 2]:  # type: ignore
            p = Player.from_series(player, [])
            p.write_streamlit_rep(
                info_only=True, show_avatars=show_avatars, show_inst=show_inst_pics
            )
with tabs[0]:
    # hf.st_style_df_with_team_vals(filtered_players, hf.DATA_NOW)
    st.info(
        "Note that you can search this table, there should be a button in the upper right for that. Also, you can sort by any of the columns, just click on the header. :)",
        icon="ℹ️",
    )
    cols = [
        "nickname",
        "has_paid_fee",
        "has_confirmed",
        "attended_before",
        "institute",
    ] + [e.sanitized_name for e in hf.DATA_NOW.sport_events.values()]
    df = hf.DATA_NOW.players[cols]
    df.insert(0, "impath", df["nickname"].apply(hf.FpathRegistry.get_animal_pic_path))

    df = df.fillna("").sort_values("nickname")
    df["nickname"] = df["nickname"].apply(
        lambda x: x[:14] + "..." if len(x) > 14 else x
    )

    column_configs = {
        event.sanitized_name: st.column_config.Column(
            label=event.icon, help=event.name, disabled=True
        )
        for event in hf.DATA_NOW.sport_events.values()
    }
    column_configs["impath"] = st.column_config.ImageColumn("Avatar")
    column_configs["nickname"] = st.column_config.TextColumn("Nickname")
    column_configs["institute"] = st.column_config.TextColumn("Institute")
    column_configs["has_paid_fee"] = st.column_config.CheckboxColumn(
        "💸",
        help="Have we received the 2 € sign-up fee?",
    )
    column_configs["attended_before"] = st.column_config.CheckboxColumn(
        "⭐",
        help="Joins the 2nd time?",
    )
    column_configs["has_confirmed"] = st.column_config.CheckboxColumn(
        "✨",
        help="Has confirmed participation?",
    )
    st.dataframe(
        df.style,
        column_config=column_configs,
        hide_index=True,
    )

with tabs[2]:
    st.info(
        "Select the player you want to see the schedule for. Typing a name in is supported."
    )
    hf.st_display_player_schedules(
        hf.DATA_NOW.players, "full", hf.DATA_NOW.matches, schedule_only=True
    )
