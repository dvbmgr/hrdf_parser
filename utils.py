import re

import settings


class Utils:
    @classmethod
    def debug(a):
        if settings.settings['debug']:
            print(a)
        return a

    @classmethod
    def print_debug(*args, **kwargs):
        if settings.settings['debug']:
            print(*args[1:], **kwargs)

    @staticmethod
    def parse_s(code):
        return re.match("^([^\$]*)\$<1>(?:\$([^\$]*)\$<2>)?(?:\$([^\$]*)\$<3>)"
                        "?(?:\$([^\$]*)\$<4>)?(?:\$([^\$]*)\$<5>)?(?:\$([^\$]*"
                        ")\$<6>)?(?:\$([^\$]*)\$<7>)?(?:\$([^\$]*)\$<8>)?(?:\$"
                        "([^\$]*)\$<9>)?", code).groups()

    @staticmethod
    def comma_split(v):
        return list(map(lambda x: x.strip(), v.split(',')))

    @staticmethod
    def type_parser(code):
        got = re.match("(?P<fun>\w+)\((?P<args>(?:\-?[^,]+(,\s?)?)+)\)(?:@"
                       "(?P<split>\d+))?", code)
        match = got.groupdict()
        args = Utils.comma_split(match["args"])
        args[0] = int(args[0]) - 1 if args[0] else None
        args[1] = int(args[1]) if args[1] else None
        return {"fun": match['fun'],
                "args": args,
                "split": int(match['split']) if match['split'] else 0}

    @staticmethod
    def conv_float(v):
        return float(v) if v else None

    @staticmethod
    def conv_int(v):
        return int(v) if v else None
