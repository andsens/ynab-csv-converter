import os.path


__version__ = '0.0.5'


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
	formula = load_yaml(formula_path)
	validate_formula(formula)
	return formula


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
