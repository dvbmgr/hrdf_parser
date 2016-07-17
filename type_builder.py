import handler
import utils
import ini


class TypeBuilder:
    @classmethod
    def get_BUILD_LIST(cls):
        return {"bool": cls.build_bool,
                "char": cls.build_char,
                "int": cls.build_int,
                "float": cls.build_float}

    @classmethod
    def get_sliced(cls, line, args):
        return line[slice(args[0] if args[0] else None,
                          args[1] if args[1] else None)].strip()

    @classmethod
    def build_bool(cls, args, split):
        return (lambda line:
                cls.get_sliced(line, args) == args[2])

    @classmethod
    def build_char(cls, args, split=None):
        if split:
            return (lambda line:
                    utils.Utils.parse_s(cls.get_sliced(line, args))[split - 1])
        return (lambda line: cls.get_sliced(line, args))

    @classmethod
    def build_int(cls, args, split):
        return (lambda line:
                utils.Utils.conv_int(cls.get_sliced(line, args)))

    @classmethod
    def build_float(cls, args, split):
        return (lambda line:
                utils.Utils.conv_float(cls.get_sliced(line, args)))

    @classmethod
    def build_generic(cls, args, split):
        return (lambda line:
                cls.get_sliced(line, args))

    @classmethod
    def build(cls, fun, args, split):
        if fun in cls.get_BUILD_LIST():
            return cls.get_BUILD_LIST()[fun](args, split)
        return cls.build_generic(args, split)

    @classmethod
    def parse(cls, code):
        return cls.build(**utils.Utils.type_parser(code))
