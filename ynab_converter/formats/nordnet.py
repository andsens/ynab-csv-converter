
def getlines(inhandle):
	import csv
	import datetime
	import locale

	transactions = csv.reader(inhandle, delimiter=';',
	                          quotechar='"', quoting=csv.QUOTE_MINIMAL)
	locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
	conv = {'EUR': 7.46, 'USD': 6.68, 'DKK': 1}
	transactions.next()
	for line in transactions:
		if len(line) == 0:
			# export may contain empty lines
			continue
		line = map(lambda field: field.decode('iso-8859-1'), line)
		line_id = line[0]
		bogf_date = line[1]
		trns_date = line[2]
		val_date = line[3]
		trns_type = line[4]
		stock_name = line[5]
		instr_type = line[6]
		isin = line[7]
		quantity = line[8]
		price = line[9]
		interest = line[10]
		fee = line[11]
		amount = line[12]
		currency = line[13]
		buy_price = line[14]
		result = line[15]
		total_qty = line[16]
		saldo = line[17]
		exch_rate = line[18]
		trns_text = line[19]
		shred_date = line[20]
		verification_number = line[21]

		date = datetime.datetime.strptime(bogf_date, '%Y-%m-%d')
		if instr_type == 'Aktie':
			payee = u'{action} {code}'.format(action=trns_type.capitalize(), code=stock_name)
			memo = u'{qty} stk. til {cur} {price}'.format(qty=quantity, price=price, cur=currency)
		else:
			payee = trns_type.capitalize()
			memo = u''
		category = u''
		amount = locale.atof(amount) * conv[currency]
		if amount > 0:
			outflow = 0.0
			inflow = amount
		else:
			outflow = -amount
			inflow = 0.0

		yield [date, payee, category, memo, outflow, inflow]
