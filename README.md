Tool to generate random [ADM](https://asterixdb.apache.org/docs/0.9.8/datamodel.html) datasets that can be used for testing.
Relies on a hacky usage of Python's JSON encoder and regex so expect your computer to explode randomly if you use this tool.

### Usage
```
usage: generator.py [-h] -n NUM_RECORDS -o OUTPUT [-p] [-s SEED] [-c SHARES SHARES SHARES]

options:
  -h, --help            show this help message and exit
  -n NUM_RECORDS, --num-records NUM_RECORDS
                        the number of records to be generated
  -o OUTPUT, --output OUTPUT
                        output file
  -p, --pretty-print    pretty print generated output
  -s SEED, --seed SEED  seed for random number generator
  -c SHARES SHARES SHARES, --shares SHARES SHARES SHARES
                        approximate share of primitive, incomple information, and derived types in the records respectively
```

### Dependencies
* Python 3
* [`numpy`](https://pypi.org/project/numpy/)
