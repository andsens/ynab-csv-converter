# -*- coding: utf-8 -*-
import re
from collections import namedtuple

HypoVereinsbankLine = namedtuple('HypoVereinsbankLine', ['account_no', 'date', 'txn_date',
                                                         'payee1', 'payee2', 'text',
                                                         'amount', 'currency'])
date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
column_patterns = {'account_no': r'^\d+$',
                   'date':       date_pattern,
                   'txn_date':   date_pattern,
                   'payee1':     r'^.*$',
                   'payee2':     r'^.*$',
                   'text':       r'^.*$',
                   'amount':     r'^-?\d{1,3}(\.\d{3})*,\d{2}$',
                   'currency':   r'^[A-Z]{3}$',
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}


def getlines(path):
    from ynab_csv_converter.unicode_csv import UnicodeReader
    import csv
    import datetime
    import locale
    from . import validate_line
    from ynab import YnabLine

    with open(path) as handle:
        transactions = UnicodeReader(handle, encoding='iso-8859-1',
                                     delimiter=';', quotechar='"',
                                     quoting=csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

        # Skip headers
        transactions.next()
        line_no = 1
        for raw_line in transactions:
            line_no += 1
            try:
                line = HypoVereinsbankLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d.%m.%Y')
                payee = line.payee1.capitalize()
                category = u''
                memo = u''
                if len(payee) == 0:
                    payee = line.text.capitalize()
                else:
                    memo = line.text.capitalize()
                if len(line.payee2) > 0:
                    memo += u' Empfänger 2: ' + line.payee2.capitalize()
                amount = locale.atof(line.amount)
                if amount > 0:
                    outflow = 0.0
                    inflow = amount
                else:
                    outflow = -amount
                    inflow = 0.0
            except:
                import sys
                msg = ("There was a problem on line {line} in {path}\n"
                       .format(line=line_no, path=path))
                sys.stderr.write(msg)
                raise

            yield YnabLine(date, payee, category, memo, outflow, inflow)
