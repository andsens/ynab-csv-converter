import sys

def convert(informat, inhandle, outhandle, otheropts):
	consolidation_txns = []
	if 'consolidate' in otheropts:
		from formats import ynab
		with open(otheropts['consolidate']) as consolidate_handle:
			consolidation_txns = list(ynab.getlines(consolidate_handle))

	from unicode_writer import UnicodeWriter
	import csv
	transactions_out = UnicodeWriter(outhandle, delimiter=',',
	                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)
	transactions_out.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])
	factor = otheropts.get('factor', 1)
	written = 0
	for line in informat.getlines(inhandle):
		[date, payee, category, memo, outflow, inflow] = line
		outflow = float(outflow) * factor
		inflow = float(inflow) * factor

		if line in consolidation_txns:
			continue
		transactions_out.writerow([
			date.strftime('%d/%m/%Y'),
			payee,
			category,
			memo,
			str(format(outflow, '.2f')),
			str(format(inflow, '.2f'))
		])
		written += 1
	sys.stderr.write('Wrote {count} transactions.\n'.format(count=written))
