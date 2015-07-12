
def getlines(inhandle):
	import datetime
	import csv

	transactions = csv.reader(inhandle, delimiter=',',
	                          quotechar='"', quoting=csv.QUOTE_MINIMAL)
	transactions.next()
	for line in transactions:
		[date, payee, category, memo, outflow, inflow] = map(lambda field: field.decode('utf-8'), line)
		date = datetime.datetime.strptime(date, '%d/%m/%Y')
		outflow = float(outflow)
		inflow = float(inflow)
		yield [date, payee, category, memo, outflow, inflow]
