import re


def getlines(inhandle):
	import csv
	import datetime
	import locale

	transactions = csv.reader(inhandle, delimiter=';',
	                          quotechar='"', quoting=csv.QUOTE_ALL)
	locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
	transactions.next()
	for line in transactions:
		[date, text, amount, saldo, status, afstemt] = map(lambda field: field.decode('iso-8859-1'), line)
		date = datetime.datetime.strptime(date, '%d.%m.%Y')
		payee, memo = parse_text(text)
		category = u''
		amount = locale.atof(amount)
		if amount > 0:
			outflow = 0
			inflow = amount
		else:
			outflow = -amount
			inflow = 0

		yield [date, payee, category, memo, outflow, inflow]


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
