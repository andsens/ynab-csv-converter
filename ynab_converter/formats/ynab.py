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
	from ynab_converter.unicode_csv import UnicodeReader
	import csv
	import datetime
	from . import validate_line

	with open(path) as handle:
		transactions = UnicodeReader(handle, delimiter=',',
		                             quotechar='"', quoting=csv.QUOTE_MINIMAL)
		# Skip headers
		transactions.next()
		line_no = 1
		for raw_line in transactions:
			line_no += 1
			try:
				# No need to encode, ynab files are already in utf-8
				line = YnabLine(*raw_line)
				validate_line(line, column_patterns)

				date = datetime.datetime.strptime(line.date, '%d/%m/%Y')
				outflow = float(line.outflow)
				inflow = float(line.inflow)
			except:
				import sys
				msg = ("There was a problem on line {line} in {path}\n"
				       .format(line=line_no, path=path))
				sys.stderr.write(msg)
				raise
			yield YnabLine(date, line.payee, line.category, line.memo, outflow, inflow)


def putlines(path, lines):
	from ynab_converter.unicode_csv import UnicodeWriter
	import csv

	with open(path, 'w') as handle:
		transactions_out = UnicodeWriter(handle, delimiter=',',
		                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)
		transactions_out.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])
		for line in lines:
			transactions_out.writerow([line.date.strftime('%d/%m/%Y'),
				                         line.payee,
				                         line.category,
				                         line.memo,
				                         str(format(line.outflow, '.2f')),
				                         str(format(line.inflow, '.2f')),
			                           ])
