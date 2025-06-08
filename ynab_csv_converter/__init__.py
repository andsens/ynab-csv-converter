"""ynab-csv-converter
convert: Convert transactionlists from various bank formats to the nYNAB format
consolidate: Combine all converted files from a formula into one single file

Usage:
  ynab-csv-converter [options] convert FORMULA INFILE...
  ynab-csv-converter [options] consolidate FORMULA

Options:
  -h, --help   show this help
  -d, --debug  print debug messages (e.g. include stacktrace in errors)

Supported formats:
  nordnet              nordnet.dk ("XLS compatible")
  sparekassen          Sparekassen Kronjylland
  sparekassen-erhverv  Sparekassen Kronjylland business account
  danskebank           Danske Bank (tab separated)
  hypovereinsbank      HypoVereinsbank
  americanexpress      American Express
  starmoney            Starmoney 13
  laanspar             Lån & Spar
  eika                 Eika
  saxotradergo         Excel export from SaxoTrader Go, converted to CSV
  banknordik           BankNordik
"""

import os.path


__version__ = '1.0.1'


def load_yaml(path):
    import yaml
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def validate_formula(formula):
    import jsonschema
    schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'formula-schema.yml'))

    schema = load_yaml(schema_path)
    try:
        jsonschema.validate(formula, schema)
    except jsonschema.ValidationError as e:
        raise FormulaError(e.message, formula, e.path)


def load_formula(formula_path):
    from . import load_yaml
    from . import validate_formula
    import importlib
    formula = load_yaml(formula_path)
    validate_formula(formula)
    module_name = 'ynab_csv_converter.formats.' + formula['format']
    module = importlib.import_module(module_name)
    return formula, module


class FormulaError(Exception):
    def __init__(self, message, settings_path, data_path=None):
        super(FormulaError, self).__init__(message)
        self.message = message
        self.settings_path = settings_path
        self.data_path = data_path

    def __str__(self):
        if self.data_path is not None:
            path = '.'.join(map(str, self.data_path))
            return ('{msg}\n  File path: {file}\n  Data path: {datapath}'
                    .format(msg=self.message, file=self.settings_path, datapath=path))
        return '{file}: {msg}'.format(msg=self.message, file=self.settings_path)
