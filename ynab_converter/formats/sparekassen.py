
def getlines(inhandle):
	import csv
	import datetime
	import locale
	transactions = csv.reader(inhandle, delimiter=';',
	                          quotechar='"', quoting=csv.QUOTE_MINIMAL)
	locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
	for line in transactions:
		[date, _, text, amount, saldo] = map(lambda field: field.decode('iso-8859-1'), line)
		date = datetime.datetime.strptime(date, '%d-%m-%Y')
		payee = text
		category = u''
		memo = u''
		amount = locale.atof(amount)
		if amount > 0:
			outflow = 0
			inflow = amount
		else:
			outflow = -amount
			inflow = 0

		yield [date, payee, category, memo, outflow, inflow]
