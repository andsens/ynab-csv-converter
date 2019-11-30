#!/usr/bin/env python3


def main():
    import docopt
    from . import __doc__ as doc
    opts = docopt.docopt(doc)
    try:
        if opts['consolidate']:
            consolidate(opts)
        if opts['convert']:
            convert(opts)
    except Exception as e:
        if opts['--debug']:
            raise
        import sys
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)


def consolidate(opts):
    from . import load_formula
    from .formats import ynab
    import os
    from itertools import chain
    formula, formula_module = load_formula(opts['FORMULA'])

    out_prefix = os.path.join(formula['outpath'], formula['outprefix'])

    # Get all files that were converted with this formula
    converted_files = sorted(find_files(out_prefix), reverse=formula_module.txn_date_descends)
    all_converted = [file[0] for file in converted_files]
    if len(all_converted) < 2:
        raise Exception('There must be at least 2 files to consolidate')

    # Get all lines from those converted files
    all_lines = list(chain(*(ynab.getlines(path) for path in all_converted)))

    if len(all_lines) > 0:
        output_filepath, fromdate, todate, increment = get_filename_parts(out_prefix, all_lines)

        # Write import lines to outputfile
        with ynab.write_file(output_filepath) as put_line:
            for line in all_lines:
                put_line(line)

        print("Wrote {written} transactions to {path}"
              .format(written=len(all_lines),
                      read=len(all_lines),
                      path=output_filepath))
    else:
        print("No transactions found for formula `{}'".format(opts['FORMULA']))

    # Remove all files that have been consolidated
    for converted in all_converted:
        os.remove(converted)


def convert(opts):
    from . import load_formula
    from .formats import ynab
    import os.path
    import shutil
    from itertools import chain
    formula, formula_module = load_formula(opts['FORMULA'])

    out_prefix = os.path.join(formula['outpath'], formula['outprefix'])
    archive_prefix = os.path.join(formula['archivepath'], formula['outprefix'])

    for import_file in opts['INFILE']:
        # Get the lines to import
        # (and cache the list, we will iterate through it multiple times)
        all_lines = list(formula_module.getlines(import_file))

        # Find the daterange we are importing
        import_min = min([line.date for line in all_lines])
        import_max = max([line.date for line in all_lines])

        # Find previously converted files
        previously_converted = list(find_daterange(out_prefix, import_min, import_max))

        # Get all lines from those previously converted files
        prev_lines = chain(*(ynab.getlines(path) for path in previously_converted))

        # Filter previous lines to only contain transactions inside the import daterange
        # (also cache this one, we do multiple lookups)
        consolidation_lines = list([line for line in prev_lines if import_min <= line.date <= import_max])

        # Multiply import lines by "factor"
        all_lines = list([factor_line(line, formula.get('factor', 1)) for line in all_lines])

        # Filter import lines using the previously converted transactions
        unique_lines = [line for line in all_lines if line not in consolidation_lines]

        if len(unique_lines) > 0:
            output_filepath, fromdate, todate, increment = get_filename_parts(out_prefix, unique_lines)

            # Write import lines to outputfile
            with ynab.write_file(output_filepath) as put_line:
                for line in unique_lines:
                    put_line(line)

            print("Wrote {written} out of {read} transactions to {path}"
                  .format(written=len(unique_lines),
                          read=len(all_lines),
                          path=output_filepath))
        else:
            print("No unique lines found in {path}".format(path=import_file))

        # Archive original file (use the total daterange for the filename)
        date_suffix = '-' + import_max.strftime('%Y%m%d') + '-' + import_min.strftime('%Y%m%d')
        archive_filepath = archive_prefix + date_suffix + '.csv'
        increment = 0
        while os.path.exists(archive_filepath):
            increment += 1
            archive_filepath = archive_prefix + date_suffix + '-' + str(increment) + '.csv'
        shutil.move(import_file, archive_filepath)


def factor_line(line, factor):
    from .formats.ynab import YnabLine
    return YnabLine(line.date, line.payee, line.category, line.memo,
                    round(factor * line.outflow, 2), round(factor * line.inflow, 2))


def find_daterange(prefix, min_date, max_date):
    for path, fromdate, todate, increment in find_files(prefix):
        if fromdate <= max_date and todate >= min_date:
            yield path


def find_files(prefix):
    import datetime
    import re
    import glob
    file_pattern = re.compile(
        r'^' + re.escape(prefix) + r'\-(?P<to>\d{8})\-(?P<from>\d{8})(\-(?P<inc>\d+))?\.csv$')
    for path in glob.glob(prefix + '-' + '[0-9]' * 8 + '-' + '[0-9]' * 8 + '*.csv'):
        result = file_pattern.match(path)
        if result is None:
            raise Exception('Found file that does not match pattern: ' + path)
        fromdate = datetime.datetime.strptime(result.group('from'), '%Y%m%d')
        todate = datetime.datetime.strptime(result.group('to'), '%Y%m%d')
        increment = None
        if result.group('inc') is not None:
            increment = int(result.group('inc'))
        yield path, fromdate, todate, increment


def get_filename_parts(out_prefix, lines):
    import os.path
    # Find the daterange in the lines supplied and create the name for the output file with that
    # We reverse the date order so that the files are sorted by newest transaction
    fromdate = min([line.date for line in lines])
    todate = max([line.date for line in lines])
    date_suffix = '-' + todate.strftime('%Y%m%d') + '-' + fromdate.strftime('%Y%m%d')
    output_filepath = out_prefix + date_suffix + '.csv'
    # Handle duplicate filenames by tacking on an increment counter
    increment = 0
    while os.path.exists(output_filepath):
        increment += 1
        output_filepath = out_prefix + date_suffix + '-' + str(increment) + '.csv'
    return output_filepath, fromdate, todate, increment


if __name__ == '__main__':
    main()
