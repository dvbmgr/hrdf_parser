import os

settings = {"basepath": "../",
            "tables": "../structs/tables.ini",
            "attributes": "../structs/attributes.ini",
            "data": "data/",
            "debug": True,
            "database": "../database.db",
            "recursion": 20000000,
            "progressbar": True,
            "table": "tables"}


def get_path_data(data):
    return os.path.join(settings['basepath'], settings['data'], data)
