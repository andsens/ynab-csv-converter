# -*- coding: utf-8 -*-
import re
from collections import namedtuple

SaxoTraderGoLine = namedtuple('SaxoTraderGoLine', [
    'account_id',
    'posting_date',
    'value_date',
    'product',
    'net_change',
    'cash_balance'
])
date_pattern = r'^[0123]\d-([01]\d|[a-z]{3})-[12]\d{3}$'
amount_pattern = r'^-?\d+(\.\d{1,2})?$'
# 'account_id': r'^\d{6}INET$',
column_patterns = {'posting_date': date_pattern,
                   'value_date': date_pattern,
                   # 'product': ,
                   'net_change': amount_pattern,
                   'cash_balance': amount_pattern,
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}
txn_date_descends = True


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='utf-8') as handle:
        transactions = csv.reader(handle, delimiter=',', quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        # Skip headers
        next(transactions)
        for raw_line in transactions:
            try:
                line = SaxoTraderGoLine(*raw_line)
                validate_line(line, column_patterns)

                try:
                    date = datetime.datetime.strptime(line.value_date, '%d-%m-%Y')
                except ValueError:
                    date = datetime.datetime.strptime(line.value_date, '%d-%b-%Y')
                payee, memo = parse_text(line.product)
                category = u''
                amount = locale.atof(line.net_change)
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
    result = re.match(r'^(?P<payee>.+) (?P<txnid>\d{9,})$', text)
    if result is not None:
        matches = result.groupdict()
        return matches['payee'], '{payee} txn #{txnid}'.format(payee=matches['payee'], txnid=matches['txnid'])
    else:
        return text, u''
