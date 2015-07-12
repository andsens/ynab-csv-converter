import re
from collections import namedtuple

SparekassenLine = namedtuple('YnabLine', ['date', 'txndate', 'text', 'amount', 'balance'])
amount_pattern = r'^-?\d{1,3}(\.\d{3})*,\d{2}$'
date_pattern = r'^\d{2}-\d{2}-\d{4}$'
column_patterns = {'date':    date_pattern,
                   'txndate': date_pattern,
                   'text':    r'^.+$',
                   'amount':  amount_pattern,
                   'balance': amount_pattern,
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}


def getlines(path):
	from ynab_converter.unicode_csv import UnicodeReader
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

		line_no = 0
		for raw_line in transactions:
			line_no += 1
			try:
				line = SparekassenLine(*raw_line)
				validate_line(line, column_patterns)

				date = datetime.datetime.strptime(line.date, '%d-%m-%Y')
				payee = line.text
				category = u''
				memo = u''
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
