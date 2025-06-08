import re
from collections import namedtuple

SparekassenLine = namedtuple('SparekassenLine', ['date', 'text', 'payee_text', 'amount', 'orig_amount'])
amount_pattern = r'^-?\d{1,3}(\.\d{3})*,\d{2}$'
date_pattern = r'^\d{2}/\d{2}/\d{4}$'
iso_currency_pattern = r'[A-Z]{3}'
column_patterns = {'date':    date_pattern,
                   'text':    r'^(.|\n)+$',
                   'payee_text':    r'^(.|\n)*$',
                   'amount':  amount_pattern,
                   'orig_amount': amount_pattern + r'|^$'
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}
txn_date_descends = True


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='utf-8-sig') as handle:
        transactions = csv.reader(handle, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

        for raw_line in transactions:
            try:
                if len(raw_line) == 6:
                    # business accounts also export the original amount, ignore it
                    raw_line = raw_line[0:2] + raw_line[3:6]
                line = SparekassenLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d/%m/%Y')
                payee = line.text
                category = ''
                memo = line.payee_text
                amount = locale.atof(line.amount)
                if amount > 0:
                    outflow = 0.0
                    inflow = amount
                else:
                    outflow = -amount
                    inflow = 0.0
            except Exception:
                import sys
                msg = ("There was a problem on line {line} in {path}\n"
                       .format(line=transactions.line_num, path=path))
                sys.stderr.write(msg)
                raise

            yield YnabLine(date, payee, category, memo, outflow, inflow)
