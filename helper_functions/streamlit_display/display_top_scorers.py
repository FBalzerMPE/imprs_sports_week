###################################################################
### INDIVIDUAL TOP SCORERS

import pandas as pd
import streamlit as st

from ..constants import SPORTS_LIST, FpathRegistry
from ..data_registry import DataRegistry
from ..util import register_or_add_to_dict
from .streamlit_util import st_style_df_with_team_vals


def _get_individual_score_df(
    data: DataRegistry, num_to_cut_to: int = 10
) -> pd.DataFrame:
    winner_dict: dict[str, float] = dict()
    for match in data.matches:
        win_val = data.sport_events[match.sport].single_match_win_value
        for win_player in match.winning_players:
            register_or_add_to_dict(winner_dict, win_player, win_val)
        for tie_player in match.tying_players:
            register_or_add_to_dict(winner_dict, tie_player, win_val / 2)

    for team_letter in data.team_letters:
        win_val = (
            data.get_running_sprints_score(team_letter)
            / data.sport_events["running_sprints"].num_players_per_subteam
        )
        for player in data.subteams[f"running_sprints_{team_letter}1"].players:
            register_or_add_to_dict(winner_dict, player, win_val)

    players: pd.DataFrame = data.players.infer_objects(True).fillna("")  # type: ignore
    players["Score_num"] = players["nickname"].apply(lambda x: winner_dict.get(x, 0))
    players["Sports"] = players.apply(
        lambda x: [
            sport
            for sport in SPORTS_LIST
            if x.get(f"subteam_{sport}", "") not in ["", "R"]
        ],
        axis=1,
    )
    players["Sports"] = players["Sports"].apply(
        lambda sports: " ".join([data.sport_events[s].icon for s in sports])
    )
    players["Team"] = players["Team"].str.replace("Team ", "")
    top_ten = (
        players[["nickname", "Team", "Score_num", "Sports"]]
        .sort_values("Score_num", ascending=False)
        .iloc[:num_to_cut_to]
        .reset_index(drop=True)
    )
    top_ten.insert(0, "Place", range(1, num_to_cut_to + 1))
    top_ten["avatar"] = top_ten["nickname"].apply(FpathRegistry.get_animal_pic_path)
    top_ten["Score"] = top_ten["Score_num"].apply(lambda x: f"{x:.1f}")
    # We only want to reveal the top ten
    return top_ten.rename(columns={"nickname": "Nickname"})


_SCORER_TEXT = """
What do these scores mean and how are they calculated, you ask?\\
They roughly reflect how many points these individuals have solely achieved for their team - roughly speaking, by winning a single match, you'd score your team between 4 and 6.5 points!

We calculate the score $S$ by summing the winning values, $S=\\sum_{{i}}(w_i + t_i/2)X_i$, where $w_i$ and $t_i$ are the amounts of games won and tied for each attended sport $i$, and $X_i$ is the contribution value of a single player for a single match in sport $i$.\\
We determine $X_i=\\frac{{100f_i}}{{N_{{{{\\rm match}},i}}N_{{{{\\rm pps}}, i}}}}$, where $f_i$ is the point-weight factor of sport $i$ that can also be seen in the plot for the results, $N_{{{{\\rm match}},i}}$ the number of matches scheduled for sport $i$, and $N_{{{{\\rm pps}},i}}$ is the number of players per subteam, so e.g. for Football, $X_{{\\rm F}}=2\\cdot100/(3\\cdot7\\cdot2)\\approx4.8$, and for chess $X_{{\\rm C}}=100/(18\\cdot1)=5.55$.\\
Note that we divide by the planned number of players in a subteam and not the actual one, to even things out; you get the same amount of points for winning in football in a team of just the planned 7 as in a team of 10.

Also note that these values differ for each Sports Week, as the number of matches, players per subteam, and point weight factors can change - e.g., in the first Sports Week, Chess and Tennis were worth 11.1 points as there were very little matches.\\
"""


def st_display_top_scorers(data: DataRegistry):
    if not data.has_scores:
        st.write(
            "The top scorers will only be revealed at the very end of the sports week. Just do your best and you might end up in the top 50!"
        )
        return
    score_df = _get_individual_score_df(data, 50)
    col_config = {"avatar": st.column_config.ImageColumn("")}
    # The formatted 'score' column is a relic before I had the progress bar.
    col_config["Score_num"] = st.column_config.ProgressColumn(
        "Score", max_value=max(score_df["Score_num"]), format=""
    )
    st.write(
        f"The table below shows the top-scoring players of the {data.year} sports week!"
    )
    st.dataframe(
        st_style_df_with_team_vals(score_df, data),
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
    st.write(_SCORER_TEXT.replace("YEAR", str(data.year)))
