"""
An Eika, or SDC portalbank, module for attempting some smart extraction

This module was primarily created for customers of a bank that is part of Eika's cooperation, which uses the danish
SDC "portalbank" solution. Exports from all banks from there should follow the same conventions, but your mileage may
vary.

The module makes a lot of assumptions, and as such should be used on a very, small set of transactions initially.
Once you've established some trust, and confirmed that my assumptions also hold for use-case, then feel free to help
tidy up or come with suggestions.

This module is to be considered untested, unstable, alpha, et cetera.

.. module:: eika

.. moduleauthor:: Thor K. Høgås <thor at roht no>


"""

import re
from collections import namedtuple

EikaLine = namedtuple('EikaLine', ['date', 'txndate', 'text', 'amount', 'balance'])
amount_pattern = r'^-?\d{1,3}(\.\d{3})*,\d{2}$'
date_pattern = r'^\d{2}\.\d{2}\.\d{4}'
text_date_pattern = r'\d{4}-\d{2}-\d{2}$'
column_patterns = {'date':    date_pattern,
                   'txndate': date_pattern,
                   'text':    r'^.+$',
                   'amount':  amount_pattern,
                   'balance': amount_pattern,
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='utf-8-sig') as handle:
        transactions = csv.reader(handle, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_ALL)
        locale.setlocale(locale.LC_ALL, 'nb_NO.UTF-8')

        for raw_line in transactions:
            try:
                line = EikaLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d.%m.%Y')
                payee = line.text
                category = ''
                memo = ''

                # Extra cool parsing, because of this shitty export
                if re.match(r'^Varekjøp', line.text):
                    payee = re.search(r'(?<=Varekjøp ).+?(?= betal dato)', line.text)[0]
                    date = datetime.datetime.strptime(re.search(text_date_pattern, line.text)[0], '%Y-%m-%d')

                elif re.match(r'^VISA VARE', line.text):
                    m = re.search(r'(?<=VISA VARE \w{16} )(?P<date>\d{2}.\d{2})  ?(?P<cost>\w{0,3} ?\d*?,?\d*?) (?P<payee>.+?) (?=Kurs)', line.text)
                    m = m if m is not None \
                        else re.search(r'(?<=VISA VARE \w{16} )(?P<date>\d{2}.\d{2})  ?(?P<cost>\w{0,3} ?\d*?,?\d*?) (?P<payee>.+)', line.text)
                    m = m if m is not None \
                        else re.search(r'(?<=VISA VARE \w{16} )(?P<date>\d{2}.\d{2})  ?(?P<payee>.+)', line.text)
                    transaction = m.groupdict()
                    payee = transaction.get('payee', line.text)
                    memo = transaction.get('cost', '') if transaction.get('cost') != '0,00' else ''

                elif re.match(r'Lønn', line.text):
                    payee = re.search(r'(?<=Lønn - ).*', line.text)[0]

                else:
                    payee = line.text

                amount = locale.atof(line.amount.replace('.', ''))
                if amount > 0:
                    outflow = 0.0
                    inflow = amount
                else:
                    outflow = -amount
                    inflow = 0.0
            except Exception as e:
                import sys
                msg = ("There was a problem on line {line} in {path}, Python line {line_code}\n"
                       .format(line=transactions.line_num, path=path, line_code=sys.exc_info()[2].tb_lineno))
                sys.stderr.write(raw_line[2] + "\n")
                sys.stderr.write(msg)
                raise e

            yield YnabLine(date, payee, category, memo, outflow, inflow)
