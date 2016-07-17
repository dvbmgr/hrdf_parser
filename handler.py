import re

import settings
import utils


def kt(v):
    if type(v).__name__ == 'bool':
        return 1 if v else 0
    return v


class BaseHandler:
    _ignore_fields = ["_ignore_fields", "_fields_types",
                      "_all_attrs", "_attributes", "sql_create"]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._fields_types:
                setattr(self, key, value)
        self._all_attrs = kwargs.keys()

    def __repr__(self):
        return self.__class__.__name__ + "(" + (",".join(
            key + "=" + repr(getattr(self, key)) for key in self._attributes)
                                                ) + ")"

    @property
    def _attributes(self):
        return [x for x in self._all_attrs if x not in self._ignore_fields]

    @classmethod
    def sql_create(cls):
        def _get_len(args):
            if args[0] is None or args[1] is None:
                return 255
            return args[1]-args[0]

        def get_type(tp):
            leng = _get_len(tp['args'])
            if tp['fun'] == 'int':
                return 'INTEGER'
            elif tp['fun'] == 'float':
                return 'FLOAT'
            elif tp['fun'] == 'char':
                return 'VARCHAR({leng})'.format(leng=leng)
            elif tp['fun'] == 'bool':
                return 'INTEGER'
            else:
                return 'VARCHAR({leng})'.format(leng=leng)

        return "CREATE TABLE IF NOT EXISTS {tablename} ( {columns} )".format(
            tablename=settings.settings['table'] + "_" + cls.__name__.lower(),
            columns=", ".join(
                repr(kr) + " " + get_type(kv) for kr, kv
                    in cls._fields_types.items()))

    @classmethod
    def sql_insert_many(cls, values):
        def _get_proper_value(value, kr):
            if getattr(value, kr) is None:
                return 'NULL'
            return repr(kt(getattr(value, kr)))
        field_types = set(cls._fields_types.keys())
        return ("INSERT INTO {tablename} ( {columns} )"
               "VALUES ( {values} )").format(
            tablename=settings.settings['table'] + "_" + cls.__name__.lower(),
            columns=", ".join(repr(kr) for kr in field_types),
            values=" ),  ( ".join(
                ", ".join(_get_proper_value(value, kr) for kr in field_types)
                    for value in values))

    @property
    def sql_insert(self):
        return self.__class__.sql_insert_many([self])

    @classmethod
    def sql_drop(cls):
        return "DROP TABLE {tablename}".format(
            tablename=settings.settings['table'] + "_" + cls.__name__.lower())


class NoneHandler(BaseHandler):
    @classmethod
    def sql_create(cls):
        return ""

    @classmethod
    def sql_insert_many(cls):
        return ""


def get_class(ini, section):
    if "_line_types" in ini.get_fields(section):
        return type(section.title(), (NoneHandler,), {})
    return type(section.title(),
                (BaseHandler,),
                {'_fields_types': {tu: utils.Utils.type_parser(tv) for tu, tv
                                   in ini.get_visible_fields(section).items()},
                 **{tu: None for tu in ini.get_visible_fields(section).keys()}}
                )
