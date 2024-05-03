import pandas as pd
import streamlit as st

from .constants import SPORTS_LIST, FpathRegistry
from .data_registry import ALL_MATCHES, ALL_SUBTEAMS, get_players
from .sport_event_registry import SPORTS_EVENTS
from .streamlit_util import st_style_df_with_team_vals
from .util import register_or_add_to_dict


def _get_individual_score_df() -> pd.DataFrame:
    winner_dict: dict[str, float] = dict()
    for match in ALL_MATCHES:
        win_val = SPORTS_EVENTS[match.sport].single_match_win_value
        for win_player in match.winning_players:
            register_or_add_to_dict(winner_dict, win_player, win_val)
        for tie_player in match.tying_players:
            register_or_add_to_dict(winner_dict, tie_player, win_val / 2)

    for team_letter in "ABC":
        win_val = {"B": 35, "C": 34, "A": 31}[team_letter] / SPORTS_EVENTS[
            "running_sprints"
        ].num_players_per_subteam
        for player in ALL_SUBTEAMS[f"running_sprints_{team_letter}: 1"].players:
            register_or_add_to_dict(winner_dict, player, win_val)

    players: pd.DataFrame = get_players().infer_objects(True).fillna("")  # type: ignore
    players["Score_num"] = players["nickname"].apply(lambda x: winner_dict.get(x, 0))
    players["Sports"] = players.apply(
        lambda x: [
            sport for sport in SPORTS_LIST if x[f"subteam_{sport}"] not in ["", "R"]
        ],
        axis=1,
    )
    players["Sports"] = players["Sports"].apply(
        lambda sports: " ".join([SPORTS_EVENTS[s].icon for s in sports])
    )
    players["Team"] = players["Team"].str.replace("Team ", "")
    top_ten = (
        players[["nickname", "Team", "Score_num", "Sports"]]
        .sort_values("Score_num", ascending=False)
        .iloc[:10]
        .reset_index(drop=True)
    )
    top_ten.insert(0, "Place", range(1, 11))
    top_ten["avatar"] = top_ten["nickname"].apply(FpathRegistry.get_animal_pic_path)
    top_ten["Score"] = top_ten["Score_num"].apply(lambda x: f"{x:.1f}")
    # We only want to reveal the top ten
    return top_ten.rename(columns={"nickname": "Nickname"})


_SCORER_TEXT = """The table above shows the top-scoring players!\\
What do these scores mean and how are they calculated, you ask?\\
Well, they roughly reflect how many points these individuals have solely achieved for their team!

We calculate the score $S$ by summing the winning values, $S=\\sum_{{i}}(w_i + t_i/2)X_i$, where $w_i$ and $t_i$ are the amounts of games won and tied for each attended sport $i$, and $X_i$ is the contribution value of a single player for a sport.\\
We determine $X_i=\\frac{{100f_i}}{{N_{{{{\\rm match}},i}}N_{{{{\\rm pps}}, i}}}}$, where $f_i$ is the point-weight factor that can also be seen in the plot above, $N_{{{{\\rm match}},i}}$ the number of matches scheduled for sport $i$, and $N_{{{{\\rm pps}},i}}$ is the number of players per subteam, so e.g. for football, $X_{{\\rm F}}=150/(3\\cdot8)=6.25$, and for chess $X_{{\\rm C}}=100/(9\\cdot1)=11.1$.
As mentioned above, the sports value the individual players slightly differently, but that is fine; it's all in the range between $5.5$ and $11.1$.\\
Note that we divide by the planned number of players in a subteam and not the actual one, to even things out; you get the same amount of points for winning in football in a team of just the planned 8 as in a team of 10.
"""


def st_display_top_scorers():
    score_df = _get_individual_score_df()
    col_config = {"avatar": st.column_config.ImageColumn("")}
    # The formatted 'score' column is a relic before I had the progress bar.
    col_config["Score_num"] = st.column_config.ProgressColumn(
        "Score", max_value=max(score_df["Score_num"]), format=""
    )
    st.write("### Top Scorers")
    st.dataframe(
        st_style_df_with_team_vals(score_df),
        hide_index=True,
        column_config=col_config,
        column_order=[
            "Place",
            "Team",
            "avatar",
            "Nickname",
            "Score_num",
            "Sports",
        ],
    )
    st.write(_SCORER_TEXT)
