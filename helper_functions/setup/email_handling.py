import pandas as pd

MAIL_DICT = {
    "1": "mpe.mpg.de",
    "2": "mpa-garching.mpg.de",
    "3": "usm.lmu.de",
    "4": "eso.org",
    "5": "physik.lmu.de",
    "6": "hm.edu",
    "7": "ipp.mpg.de",
}


def get_schedule_for_player(player: pd.Series) -> str:
    """Write a schedule for the given player."""
    # TODO: Link this up with the matches
    return "Monday: Volleyball, subteam A_1 at 17:35"


def get_email_text_for_player(player: pd.Series) -> tuple[str, str]:
    first_name = player["name"].split()[0]
    nickname = player["nickname"]
    email = player["email"]
    if email != "???":
        email_key = email.split("@")[1]
        if email_key in MAIL_DICT:
            suffix = MAIL_DICT[email_key]
            email = email.replace(email_key, suffix)

    text = f"""
Dear {first_name},

thank you for filling out our survey concerning the inter-institute sports week, we're super excited to have you on board!
Please read the following carefully.

By now, we have devised a more detailed plan for the events:
All participants are grouped into three main teams that send out players for each of the sports, enabling everyone to achieve points for their main team.

With this in mind, we have already set up sub-teams for each sport, and scheduled the matches, including the ones where YOU are planned to participate.

It is therefore **really important** that you respond to this mail in case you can for whatever reason not be there to support your team. Please also respond with a brief confirmation if you can attend all just so we know you've received this mail.

Your schedule is:
{get_schedule_for_player(player)}

We have also devised a website at https://sports-week-garching.streamlit.app/
To ensure anonymity, we have provided a nickname consisiting of adjective+animal for each player;

Your nickname is
    **{nickname}**
     
This will allow you to review all of the details on the website as long as you remember the nickname. 

Be sure to briefly answer to this mail.

We hope you're as excited for the sports week as we are!

The organizing committee
Zsofi, Benny, Matteo, William, Fabi
"""
    return email, text
