import sys

import parser

pa = parser.Parser()
if len(sys.argv) > 1 and sys.argv[1] == "drop":
    pa.drop_tables()
    sys.exit()
elif len(sys.argv) > 1 and sys.argv[1] == "create":
    pa.create_tables()
    sys.exit()
pa.execute_files()
