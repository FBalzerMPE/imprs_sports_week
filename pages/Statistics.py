import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import helper_functions as hf

hf.st_set_up_header_and_sidebar()

# TODO: Refactor the plots here!
st.write(
    """On this page, you can see an overview of the results of the sports week, as well as some extra stuff to read about player numbers and so on.

## Results

For each sport, the total amount of points a main team achieved is summed up and normalized to a scale from 0 to 100.\\
We then weight each sport roughly proportional to the number of players attending - since there are more than 50 players taking part in Ping Pong, we multiply the final score for that by 2.5, while the smallest sports with only 9 attendees like Chess or Tennis only get a weight of 1. While this is of course not perfect (individual Chess games now still count a little more than individual Ping Pong games), it means that each and every game somehow matters for your team's final score.

The following plot shows the current standings, both for each of the sports individually, and finally the total score, which is just the sum of the rescaled sports scores.\\
Note that we also rescale the points by the percentage of games finished so far.\\
Let us know if you have any questions!"""
)

match_df = hf.turn_series_list_to_dataframe([m.as_series for m in hf.ALL_MATCHES])


def _calc_score_for_team(match_df: pd.DataFrame, team_letter: str, sport: str) -> float:
    assert sport in hf.SPORTS_LIST
    assert team_letter in "ABC"
    if sport == "running_sprints":
        return {"B": 35, "C": 34, "A": 31}[team_letter]

    sport_df = match_df[match_df["sport"] == sport].infer_objects(copy=False).fillna("")  # type: ignore
    num_won = np.sum(sport_df["winner"] == team_letter)
    num_tied = np.sum(
        sport_df["winner"].apply(lambda x: len(x) > 1 and team_letter in x)
    )
    return num_won + 0.5 * num_tied
    pass


sport_nums = {
    sport: [_calc_score_for_team(match_df, team, sport) for team in "ABC"]
    for sport in hf.SPORTS_LIST
}
sport_nums["Team"] = ["A", "B", "C"]  # type: ignore
df = pd.DataFrame(sport_nums).set_index("Team")
for i, sport in enumerate(hf.SPORTS_LIST):
    event = hf.SPORTS_EVENTS[sport]
    result_perc = (
        (np.round(df[sport] / df[sport].sum() * 100, 0) * event.point_weight_factor)
        if df[sport].sum() != 0
        else 0
    )
    event_matches = event.match_df.infer_objects(copy=False).fillna("")  # type: ignore
    num_tot, num_done = len(event_matches), np.sum(event_matches["winner"] != "")
    symbol = "✔️" if num_tot == num_done else ""
    colname = (
        f"{event.icon} ({num_done}/{num_tot}{symbol}) x {event.point_weight_factor:.1f}"
    )
    if sport == "running_sprints":
        colname = f"{event.icon} (✔️) x {event.point_weight_factor:.1f}"
    else:
        result_perc *= num_done / num_tot
        result_perc = round(result_perc, 1)
    df.insert(i * 2 + 1, colname, result_perc)
score_df = df[[col for col in df.columns if " x " in col]].copy()
score_df["Total Score"] = score_df.sum(axis=1)  # / score_df.sum(axis=0).sum() * 1000

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
score_df = score_df[score_df["Sport"] != "Total Score"]


team_colors = alt.Color(
    "Team:N", scale=alt.Scale(range=[team.color for team in hf.ALL_TEAMS])
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
st.altair_chart(chart, theme="streamlit", use_container_width=True)


markdown_text = hf.read_event_desc("../helper_texts/statistics")
st.markdown(markdown_text, unsafe_allow_html=True)
c = hf.create_sport_dist_altair_chart()
st.altair_chart(c, theme="streamlit", use_container_width=True)

markdown_text = hf.read_event_desc("../helper_texts/results")
