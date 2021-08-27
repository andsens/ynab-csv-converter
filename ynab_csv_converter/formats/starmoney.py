# -*- coding: utf-8 -*-
import re
from collections import namedtuple

StarMoneyLine = namedtuple('StarMoneyLine', ['date', 'txtkey', 'payee', 'memo',
                                             'category', 'costcenter', 'txnid',
                                             'splitname',
                                             'splttxncategory', 'splttxnsubcategory',
                                             'splitcostcenter', 'splitorigamount',
                                             'splitmemo1', 'splittaxrate',
                                             'splittaxamnt', 'splitfibu',
                                             'taxrate', 'taxamnt',
                                             'amount', 'balance'])
date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
column_patterns = {'date':       date_pattern,
                   'payee':      r'^.*$',
                   'memo':       r'^.*$',
                   'amount':     r'^-?\d{1,3}(\.\d{3})*,\d{2} [A-Z]{3}$',
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}
txn_date_descends = False


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='utf-8') as handle:
        transactions = csv.reader(handle, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

        # Skip headers
        next(transactions)
        for raw_line in transactions:
            try:
                line = StarMoneyLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d.%m.%Y')
                payee = line.payee.title()
                category = ''
                memo = line.memo.capitalize()
                amount = locale.atof(line.amount.replace('.', '')[0:-4])
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
