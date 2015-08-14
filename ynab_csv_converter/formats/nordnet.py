import re
from collections import namedtuple

NordnetLine = namedtuple('NordnetLine', ['line_id', 'bogf_date', 'trns_date', 'val_date', 'trns_type',
                                         'stock_name', 'instr_type', 'isin', 'quantity', 'price',
                                         'interest', 'fee', 'amount', 'currency', 'buy_price',
                                         'result', 'total_qty', 'saldo', 'exch_rate', 'trns_text',
                                         'shred_date', 'verification_number',
                                         ])
date_pattern = r'^\d{4}-\d{2}-\d{2}$'
optional_date_pattern = r'^(\d{4}-\d{2}-\d{2}|)$'
amount_pattern = r'^-?\d{1,3}(\.\d{3})*,\d{2,}$'
pos_amount_pattern = r'^\d{1,3}(\.\d{3})*,\d{2,}$'
column_patterns = {'line_id':     r'^\d{9,}$',
                   'bogf_date':   date_pattern,
                   'trns_date':   date_pattern,
                   'val_date':    date_pattern,
                   'trns_type':   r'^.+$',
                   'stock_name':  r'^.*$',
                   'instr_type':  r'^.*$',
                   'isin':        r'^.*$',
                   'quantity':    r'^(\d+|)$',
                   'price':       pos_amount_pattern,
                   'interest':    pos_amount_pattern,
                   'fee':         pos_amount_pattern,
                   'amount':      amount_pattern,
                   'currency':    r'^[A-Z]{3}$',
                   'buy_price':   pos_amount_pattern,
                   'result':      amount_pattern,
                   'total_qty':   amount_pattern,
                   'saldo':       amount_pattern,
                   'exch_rate':   pos_amount_pattern,
                   'trns_text':   r'^.*$',
                   'shred_date':  optional_date_pattern,
                   'verification_number': r'^\d{8,}$',
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
		conv = {'EUR': 7.46, 'USD': 6.68, 'DKK': 1}
		# Skip headers
		transactions.next()
		line_no = 1
		for raw_line in transactions:
			line_no += 1
			if len(raw_line) == 0:
				# export may contain empty lines
				continue
			try:
				line = NordnetLine(*raw_line)
				validate_line(line, column_patterns)

				date = datetime.datetime.strptime(line.bogf_date, '%Y-%m-%d')
				if line.instr_type == 'Aktie':
					payee = u'{action} {code}'.format(action=line.trns_type.capitalize(), code=line.stock_name)
					memo = u'{qty} stk. til {cur} {price}'.format(qty=line.quantity, price=line.price, cur=line.currency)
				else:
					payee = line.trns_type.capitalize()
					memo = u''
				category = u''
				amount = locale.atof(line.amount) * conv[line.currency]
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
