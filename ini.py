import configparser
import settings
import utils


class Ini:
    def __init__(self, sec='tables'):
        self.ini = self.__class__.read_ini(sec)

    def get_ini(self):
        return self.ini

    def get_fields(self, section):
        return dict(self.ini.items(section))

    def get_visible_fields(self, section):
        return {key: val for key, val in self.get_fields(section).items()
                if not key.startswith("_")}

    def get_value(self, section, key):
        return self.ini.get(section, key)

    def get_values(self, section, key):
        return utils.Utils.comma_split(self.ini.get(section, key))

    def is_multiline(self, section):
        return "_line_types" in self.get_fields(section)

    def get_files(self):
        return self.get_values('GENERAL', 'files')

    @classmethod
    def read_ini(cls, sec='tables'):
        utils.Utils.print_debug(
            "Reading configuration using file {file}.".format(
                file=settings.settings[sec]))
        ini = configparser.ConfigParser()
        ini._interpolation = configparser.ExtendedInterpolation()
        ini.read(settings.settings[sec])
        return ini
