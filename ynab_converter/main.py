from contextlib import contextmanager


def parse_opts():
	import docopt
	usage = """transactionlist-converter
Converts transactionlists from a format to ynab format

Usage: transactionlist-converter [options] INFORMAT

Options:
  -i, --infile <FILE>   File to read (defaults to stdin)
  -o, --outfile <FILE>  File to write (defaults to stdout)
  -x, --factor <X>      Multiplies the out-/inflow with X
                        (useful when dealing with other currencies)
  -c, --consolidate <FILE>
                        Filter output so it does not contain lines that
                        are already in FILE (must be ynab format)

Supported formats:
  nordnet      "XLS compatible" (read: csv) export from nordnet.dk
  sparekassen  Sparekassen Kronjylland netbank export
  danskebank   CSV tab-separated export from Danske Bank netbank
"""
	return docopt.docopt(usage)


@contextmanager
def open_handle(path_or_handle=None, mode='r'):
	if isinstance(path_or_handle, str):
		with open(path_or_handle, mode) as handle:
			yield handle
	else:
		yield path_or_handle


def main():
	import sys
	from convert import convert
	import importlib
	opts = parse_opts()

	inform_modname = 'ynab_converter.formats.' + opts['INFORMAT']
	informat = importlib.import_module(inform_modname)

	if opts['--infile'] is None:
		opts['--infile'] = sys.stdin
	if opts['--outfile'] is None:
		opts['--outfile'] = sys.stdout

	otheropts = {}
	if opts['--factor'] is not None:
		otheropts['factor'] = float(opts['--factor'])
	if opts['--consolidate'] is not None:
		otheropts['consolidate'] = opts['--consolidate']
	with open_handle(opts['--infile']) as inhandle:
		with open_handle(opts['--outfile'], 'w') as outhandle:
			convert(informat, inhandle, outhandle, otheropts)
