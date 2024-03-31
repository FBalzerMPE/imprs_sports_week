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
