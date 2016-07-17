import re
import sqlite3
import time
from threading import Thread


import handler
import utils
import ini
import type_builder
import settings


class Parser:
    def __init__(self, sec=settings.settings['table']):
        self.ini = ini.Ini(sec)
        self.queries = []
        self.finished = 0
        self.started = 0

    def _does_pattern_match(self, section, line):
        fields = self.ini.get_fields(section)
        if "_pattern_match" not in fields and "_starts_with" not in fields:
            return True
        if "_pattern_match" in fields:
            return re.match(self.ini.get_value(section,
                                               "_pattern_match"),
                            line)
        if "_starts_with" in fields:
            return line.startswith(self.ini.get_value(section, "_starts_with"))

    def _get_multiline_parser(self, section, line, insert=None):
        options = self.ini.get_values(section, "_line_types")
        for option in options:
            if self._does_pattern_match(option, line):
                return self.get_line_parser(option, insert)(line)
        utils.Utils.print_debug("! Unable to match {got}.".format(got=line))
        return None

    def _apply_line_parser(self, section, line, insert=None):
        if not self._does_pattern_match(section, line):
            return None
        builder = (lambda field:
                   type_builder.TypeBuilder.parse(self.ini.get_value(section,
                                                                     field)))
        field_builder = {field: builder(field)(line) for field in
                         self.ini.get_visible_fields(section)}
        parsed = handler.get_class(self.ini, section)(**field_builder)
        if insert is not None:
            return insert(parsed)
        return parsed

    def get_line_parser(self, section, insert=None):
        if section is None:
            return (lambda _: None)
        if self.ini.is_multiline(section):
            return (lambda line:
                    self._get_multiline_parser(section, line, insert))
        return (lambda line: self._apply_line_parser(section, line, insert))

    def get_file_parser(self, section, data, insert=None, progressbar=True):
        return [*map(self.get_line_parser(section, insert), data)]

    def get_empty_section_classes(self, section):
        if self.ini.is_multiline(section):
            return [*map(lambda line: handler.get_class(self.ini, line),
                         self.ini.get_values(section, "_line_types"))]
        return [handler.get_class(self.ini, section)]

    def apply_for_file(self, section, insert=None, progressbar=True):
        with open(settings.get_path_data(section), 'r') as datafile:
            data = datafile.readlines()
            threads = []
            parsed = []
            for delta in range(0, len(data), 100000):
                deltadata = data[delta:(delta+100000)]
                threads.append(Thread(target=self.get_file_parser,
                                      args=(section,
                                            deltadata,
                                            insert,
                                            progressbar)))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.finished += 1
            utils.Utils.print_debug("Done with {} !"
                                    "({}/{})".format(section,
                                                     self.finished,
                                                     self.started))
            return threads
        return None

    def _get_inserter(self):
        def add_data(data):
            self.queries.append(data.sql_insert)
        return add_data

    def insert_loop(self):
        conn = sqlite3.connect(settings.settings['database'])
        cursor = conn.cursor()
        while True:
            while self.queries:
                cursor.execute(self.queries.pop(0))
            conn.commit()
            if self.started == self.finished:
                break
        conn.close()

    def execute_file(self, section, progressbar=True):
        utils.Utils.print_debug("Starting {section}.".format(section=section))
        self.apply_for_file(section,
                            insert=self._get_inserter(),
                            progressbar=progressbar)
        utils.Utils.print_debug(
            "Finished section {section}.".format(section=section))

    def execute_files(self):
        utils.Utils.print_debug(
            "Connecting to database… {db}".format(
                db=settings.settings['database']))
        files = self.ini.get_files()
        self.started = len(files)
        threads = []
        inserter = Thread(target=self.insert_loop)
        inserter.start()
        for fle in files:
            threads.append(Thread(target=self.execute_file,
                                  args=(fle,
                                        settings.settings["progressbar"])))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        inserter.join()
        utils.Utils.print_debug("Done.")

    def create_tables(self):
        utils.Utils.print_debug(
            "Connecting to database… {db}".format(
                db=settings.settings['database']))
        conn = sqlite3.connect(settings.settings['database'])
        cursor = conn.cursor()
        for fle in self.ini.get_files():
            for section in self.get_empty_section_classes(fle):
                cursor.execute(section.sql_create())
        conn.commit()
        conn.close()
        utils.Utils.print_debug("Done.")

    def drop_tables(self):
        utils.Utils.print_debug(
            "Connecting to database… {db}".format(
                db=settings.settings['database']))
        conn = sqlite3.connect(settings.settings['database'])
        cursor = conn.cursor()
        for fle in self.ini.get_files():
            for section in self.get_empty_section_classes(fle):
                cursor.execute(section.sql_drop())
        conn.commit()
        conn.close()
        utils.Utils.print_debug("Done.")
