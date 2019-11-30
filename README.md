# YNAB CSV Converter

Converts bank record CSV files in various formats to YNAB CSV format.

Any previously converted files will be looked up so that a converted
export only contains unique transactions with respect to already
converted exports.

## Installation

```sh
pip3 install https://github.com/andsens/ynab-csv-converter/archive/master.tar.gz
```

## Usage

Usage: `ynab-csv-converter [options] FORMULA INFILE...`

## Formula

```yml
format: sparekassen
outpath: /home/andsens/converted
archivepath: /home/andsens/archive
outprefix: sparekassen-euro
factor: 7.45
```

All settings except `factor` are mandatory.
The above formula looks for converted files in `/home/andsens/converted/sparekassen-euro-[daterange]`
and removes transactions from the inputfiles that already exist in those converted
files.
All amounts are multiplied by 7.45 (EUR -> DKK).
Once converted from "sparekassen" format to "ynab" format,
the transactions are written to `/home/andsens/converted/sparekassen-euro-[daterange]`,
while the original file is archived at `/home/andsens/archive/sparekassen-euro-[daterange]`.

The `daterange` corresponds to the dates of the latest and earliest transaction
(in that order, so that newest exports are sorted last).

## Supported formats

- DanskeBank (key: danskebank)
- Sparekassen (key: sparekassen)
- Lån & Spar (key: laanspar)
- Nordnet (key: nordnet)
- HypoVereinsbank (key: hypovereinsbank)
- SaxoTraderGo Account Statement (key: saxotradergo)
