from .classes.sports_organizer import SportsOrganizer

SPORTS_ORGANIZERS = {
    "Benny": SportsOrganizer(
        name="Benny",
        nickname="Exemplary Cassowary",
        email="benecasa@2...",
        sport_keys=["volleyball", "capture_the_flag", "beer_pong"],
        is_committee_member=True,
    ),
    "David": SportsOrganizer(
        name="David",
        nickname="Disloyal Hagfish",
        email="kald@1...",
        sport_keys=["chess"],
    ),
    "Fabi": SportsOrganizer(
        name="Fabi",
        nickname="Pushy Bulldog",
        email="fbalzer@1...",
        sport_keys=["volleyball", "spikeball", "ping_pong"],
        is_committee_member=True,
    ),
    "Juan": SportsOrganizer(
        name="Juan",
        nickname="Alarmed Bird",
        email="jespejo@1...",
        sport_keys=["basketball"],
    ),
    "Matteo G": SportsOrganizer(
        name="Matteo G",
        nickname="Dishonest Fangtooth",
        email="matteani@2...",
        sport_keys=["football", "foosball"],
        is_committee_member=True,
    ),
    "Matteo B": SportsOrganizer(
        name="Matteo B",
        nickname="Animated Yak",
        email="mbordoni@1...",
        sport_keys=["tennis"],
    ),
    "William": SportsOrganizer(
        name="William",
        nickname="Magnificent Barracuda",
        email="wroster@1...",
        sport_keys=["running_sprints", "beer_pong"],
        is_committee_member=True,
    ),
    "Zsofi": SportsOrganizer(
        name="Zsofi",
        nickname="Thankful Kakapo",
        email="zigo@1...",
        sport_keys=["running_sprints", "capture_the_flag", "ping_pong"],
        is_committee_member=True,
    ),
}
