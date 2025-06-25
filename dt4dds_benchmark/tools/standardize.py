import pathlib


def standardize_dict(d):
    new_d = {}
    for key, value in d.items():
        if isinstance(value, pathlib.Path):
            new_d[key] = str(value)
        else:
            new_d[key] = value
    return new_d