from .classes.sports_organizer import SportsOrganizer

SPORTS_ORGANIZERS = {
    "Benny": SportsOrganizer(
        name="Benny",
        email="benecasa@2...",
        sport_keys=["volleyball", "capture_the_flag", "beer_pong"],
        is_committee_member=True,
    ),
    "David": SportsOrganizer(
        name="David",
        email="kald@1...",
        sport_keys=["chess"],
    ),
    "Fabi": SportsOrganizer(
        name="Fabi",
        email="fbalzer@1...",
        sport_keys=["volleyball", "spikeball", "ping_pong"],
        is_committee_member=True,
    ),
    "Juan": SportsOrganizer(
        name="Juan",
        email="jespejo@1...",
        sport_keys=["basketball"],
    ),
    "Matteo G": SportsOrganizer(
        name="Matteo G",
        email="matteani@2...",
        sport_keys=["football", "fooseball"],
        is_committee_member=True,
    ),
    "Matteo B": SportsOrganizer(
        name="Matteo B",
        email="mbordoni@1...",
        sport_keys=["tennis"],
    ),
    "William": SportsOrganizer(
        name="William",
        email="wroster@1...",
        sport_keys=["running_sprints", "beer_pong"],
        is_committee_member=True,
    ),
    "Zsofi": SportsOrganizer(
        name="Zsofi",
        email="zigo@1...",
        sport_keys=["running_sprints", "capture_the_flag", "ping_pong"],
        is_committee_member=True,
    ),
}
