import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from .constants import SPORTS_LIST, FpathRegistry
from .data_registry import (
    ALL_MATCHES,
    ALL_SUBTEAMS,
    ALL_TEAMS,
    get_match_df,
    get_players,
)
from .sport_event_registry import SPORTS_EVENTS
from .streamlit_util import st_style_df_with_team_vals
from .util import register_or_add_to_dict


def _calc_score_for_team(match_df: pd.DataFrame, team_letter: str, sport: str) -> float:
    assert sport in SPORTS_LIST
    assert team_letter in "ABC"
    if sport == "running_sprints":
        return {"B": 35, "C": 34, "A": 31}[team_letter]

    sport_df = match_df[match_df["sport"] == sport].infer_objects(copy=False).fillna("")  # type: ignore
    num_won = np.sum(sport_df["winner"] == team_letter)
    num_tied = np.sum(
        sport_df["winner"].apply(lambda x: len(x) > 1 and team_letter in x)
    )
    return num_won + 0.5 * num_tied


def _get_full_score_df() -> pd.DataFrame:
    match_df = get_match_df()
    sport_nums = {
        sport: [_calc_score_for_team(match_df, team, sport) for team in "ABC"]
        for sport in SPORTS_LIST
    }
    sport_nums["Team"] = ["A", "B", "C"]  # type: ignore
    df = pd.DataFrame(sport_nums).set_index("Team")
    for i, sport in enumerate(SPORTS_LIST):
        event = SPORTS_EVENTS[sport]
        result_perc = (
            (np.round(df[sport] / df[sport].sum() * 100, 0) * event.point_weight_factor)
            if df[sport].sum() != 0
            else 0
        )
        event_matches = event.match_df.infer_objects(copy=False).fillna("")  # type: ignore
        num_tot, num_done = len(event_matches), np.sum(event_matches["winner"] != "")
        symbol = "✔️" if num_tot == num_done else ""
        colname = f"{event.icon} ({num_done}/{num_tot}{symbol}) x {event.point_weight_factor:.1f}"
        if sport == "running_sprints":
            colname = f"{event.icon} (✔️) x {event.point_weight_factor:.1f}"
        else:
            result_perc *= num_done / num_tot
            result_perc = round(result_perc, 1)
        df.insert(i * 2 + 1, colname, result_perc)
    score_df = df[[col for col in df.columns if " x " in col]].copy()
    score_df["Total Score"] = score_df.sum(
        axis=1
    )  # / score_df.sum(axis=0).sum() * 1000

    score_df = score_df.reset_index().melt("Team", var_name="Sport", value_name="Score")

    # Add the total score for each team to the DataFrame
    total_scores = (
        score_df[score_df["Sport"] != "Total Score"].groupby("Team")["Score"].sum()
    )
    for team, total_score in total_scores.items():
        new_row = pd.DataFrame(
            {
                "Team": [team],
                "Sport": [f"Total Score {team}"],
                "Score": [total_score],
            }
        )
        score_df = pd.concat([score_df, new_row], ignore_index=True)
    return score_df[score_df["Sport"] != "Total Score"]


_RESULTS_TEXT = """For each sport, the total amount of points a main team achieved is summed up and normalized to a scale from 0 to 100.\\
We then weight each sport roughly proportional to the number of players attending - since there are more than 50 players taking part in Ping Pong, we multiply the final score for that by 2.5, while the smallest sports with only 9 attendees like Chess or Tennis only get a weight of 1. While this is of course not perfect (individual Chess games now still count a little more than individual Ping Pong games), it means that each and every game somehow matters for your team's final score.

The following plot shows the current standings, both for each of the sports individually, and finally the total score, which is just the sum of the rescaled sports scores.\\
Note that we also rescale the points by the percentage of games finished so far.\\
Let us know if you have any questions!
"""


def st_display_full_results():
    score_df = _get_full_score_df()
    team_colors = alt.Color(
        "Team:N", scale=alt.Scale(range=[team.color for team in ALL_TEAMS])
    )

    # Create the horizontal stacked bar plot
    chart = (
        alt.Chart(score_df)
        .mark_bar()
        .encode(
            y=alt.Y("Sport:N", title="", axis=alt.Axis(labelFontWeight="bold")),
            x=alt.X("Score:Q"),
            color=team_colors,
            order=alt.Order(
                # Sort the segments of the bars by this field
                "Team:N",
            ),
            opacity=alt.value(0.5),
        )
        .properties(title="Score distribution")
    )

    st.write("### Results")
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
    st.write(_RESULTS_TEXT)


###################################################################
### INDIVIDUAL TOP SCORERS


def _get_individual_score_df(num_to_cut_to: int = 10) -> pd.DataFrame:
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
        .iloc[:num_to_cut_to]
        .reset_index(drop=True)
    )
    top_ten.insert(0, "Place", range(1, num_to_cut_to + 1))
    top_ten["avatar"] = top_ten["nickname"].apply(FpathRegistry.get_animal_pic_path)
    top_ten["Score"] = top_ten["Score_num"].apply(lambda x: f"{x:.1f}")
    # We only want to reveal the top ten
    return top_ten.rename(columns={"nickname": "Nickname"})


_SCORER_TEXT = """The table above shows the top-scoring players!\\
What do these scores mean and how are they calculated, you ask?\\
They roughly reflect how many points these individuals have solely achieved for their team!

We calculate the score $S$ by summing the winning values, $S=\\sum_{{i}}(w_i + t_i/2)X_i$, where $w_i$ and $t_i$ are the amounts of games won and tied for each attended sport $i$, and $X_i$ is the contribution value of a single player for a single match in sport $i$.\\
We determine $X_i=\\frac{{100f_i}}{{N_{{{{\\rm match}},i}}N_{{{{\\rm pps}}, i}}}}$, where $f_i$ is the point-weight factor of sport $i$ that can also be seen in the plot for the results, $N_{{{{\\rm match}},i}}$ the number of matches scheduled for sport $i$, and $N_{{{{\\rm pps}},i}}$ is the number of players per subteam, so e.g. for football, $X_{{\\rm F}}=150/(3\\cdot8)=6.25$, and for chess $X_{{\\rm C}}=100/(9\\cdot1)=11.1$.
As mentioned above, the sports value the individual players slightly differently, but that is fine; it's all in the range between $5.5$ and $11.1$.\\
Note that we divide by the planned number of players in a subteam and not the actual one, to even things out; you get the same amount of points for winning in football in a team of just the planned 8 as in a team of 10.
"""


def st_display_top_scorers():
    score_df = _get_individual_score_df(25)
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
