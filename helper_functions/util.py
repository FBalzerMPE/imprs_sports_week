from .constants import DATAPATH


def sort_dict_by_values(d: dict, reverse=False) -> dict:
    """Return an instance of the given dictionary sorted by its values

    Parameters
    ----------
    d : dict
        The dictionary to sort by values

    Returns
    -------
    dict
        The sorted dictionary
    """
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def read_event_desc(event_name: str) -> str:
    fpath = DATAPATH.joinpath(f"sport_descriptions/{event_name}.md")
    if not fpath.exists():
        print("File not found:", fpath)
        return "NO DESCRIPTION FOUND"
    with fpath.open("r") as f:
        return f.read()
