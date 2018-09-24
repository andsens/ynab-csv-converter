# -*- coding: utf-8 -*-
import re
from collections import namedtuple

DanskebankLine = namedtuple('DanskebankLine', ['date', 'text', 'amount', 'balance', 'status', 'cleared'])
amount_pattern = r'^-?\d{1,3}(\.\d{3})*,\d{2}$'
column_patterns = {'date':    r'^\d{2}\.\d{2}\.\d{4}$',
                   'text':    r'^.+$',
                   'amount':  amount_pattern,
                   'balance': amount_pattern,
                   'status':  r'^Udført$',
                   'cleared': r'^(Ja|Nej)$',
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}
txn_date_descends = False


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='iso-8859-1') as handle:
        transactions = csv.reader(handle, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
        # Skip headers
        next(transactions)
        for raw_line in transactions:
            try:
                line = DanskebankLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d.%m.%Y')
                payee, memo = parse_text(line.text)
                category = u''
                amount = locale.atof(line.amount)
                if amount > 0:
                    outflow = 0.0
                    inflow = amount
                else:
                    outflow = -amount
                    inflow = 0.0
            except Exception:
                import sys
                msg = (u"There was a problem on line {line} in {path}\n"
                       .format(line=transactions.line_num, path=path))
                sys.stderr.write(msg)
                raise

            yield YnabLine(date, payee, category, memo, outflow, inflow)


def parse_text(text):
    result = re.match(r'^(?P<payee>.+\S)\s+(?P<trnsnum>\d{5})$', text)
    if result is not None:
        matches = result.groupdict()
        return matches['payee'], 'txn #{trnsnum}'.format(trnsnum=matches['trnsnum'])

    result = re.match(r'^VDK (?P<currency>[A-Z]{3})\s+(?P<amount>(\d{1,3})(\.\d{3})*,\d{2})$', text)
    if result is not None:
        matches = result.groupdict()
        payee = 'VisaDankort {currency}'.format(currency=matches['currency'])
        memo = '{currency} {amount}'.format(currency=matches['currency'], amount=matches['amount'])
        return payee, memo

    return text, u''
