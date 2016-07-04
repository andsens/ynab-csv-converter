from setuptools import setup
from setuptools import find_packages
import os.path


def find_version(path):
    import re
    version_file = open(path).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name='ynab-csv-converter',
      version=find_version(os.path.join(os.path.dirname(__file__), 'ynab_csv_converter/__init__.py')),
      packages=find_packages(),
      include_package_data=True,
      entry_points={'console_scripts': ['ynab-csv-converter = ynab_csv_converter.__main__:main']},
      install_requires=['pyyaml >= 3.10',
                        'jsonschema >= 2.3.0',
                        'docopt >= 0.6.1',
                        ],
      license='Apache License, Version 2.0',
      description='',
      long_description='''''',
      author='Anders Ingemann',
      author_email='aim@secoya.dk',
      )
