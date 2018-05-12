from contextlib import contextmanager
import re
from collections import namedtuple

YnabLine = namedtuple('YnabLine', ['date', 'payee', 'category', 'memo', 'outflow', 'inflow'])
amount_pattern = r'^\d+\.\d{2}$'
column_patterns = {'date':     r'^\d{2}/\d{2}/\d{4}$',
                   'payee':    r'^.+$',
                   'category': r'^.*$',
                   'memo':     r'^.*$',
                   'outflow':  amount_pattern,
                   'inflow':   amount_pattern,
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}


def getlines(path):
    import csv
    import datetime
    from . import validate_line

    with open(path, 'r', encoding='utf-8') as handle:
        transactions = csv.reader(handle, delimiter=',', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        # Skip headers
        next(transactions)
        for raw_line in transactions:
            try:
                line = YnabLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d/%m/%Y')
                outflow = float(line.outflow)
                inflow = float(line.inflow)
            except Exception:
                import sys
                msg = ("There was a problem on line {line} in {path}\n"
                       .format(line=transactions.line_num, path=path))
                sys.stderr.write(msg)
                raise
            yield YnabLine(date, line.payee, line.category, line.memo, outflow, inflow)


@contextmanager
def write_file(path):
    import csv
    with open(path, 'w', encoding='utf-8') as handle:
        transactions_out = csv.writer(handle, delimiter=',', quotechar='"',
                                      quoting=csv.QUOTE_MINIMAL)
        transactions_out.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])

        def putline(line):
            transactions_out.writerow([line.date.strftime('%d/%m/%Y'),
                                       line.payee,
                                       line.category,
                                       line.memo,
                                       format(line.outflow, '.2f'),
                                       format(line.inflow, '.2f'),
                                       ])
        yield putline
