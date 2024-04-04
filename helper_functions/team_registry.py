from .classes.team import Team


def get_backup_teams(num_teams: int = 3) -> list[Team]:
    """Get the teams from the backup files."""
    teams = []
    for i in range(num_teams):
        try:
            teams.append(Team.from_backup(i))
        except (FileNotFoundError, KeyError):
            pass
    return teams


ALL_TEAMS = get_backup_teams()
