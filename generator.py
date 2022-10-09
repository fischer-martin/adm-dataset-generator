#!/usr/bin/env python3

import random
import adm_types
import numpy
import argparse
import re
import sys
import contextlib



argparser = argparse.ArgumentParser()
argparser.add_argument("-n", "--num-records", help = "the number of records to be generated", type = int, required = True)
argparser.add_argument("-o", "--output", help = "output file, stdout if not specified", type = str)
argparser.add_argument("-d", "--for-direct-insertion", help = "formats type specifiers for direct insertion into datasets (contrary to usage of LOAD DATASET)", action = "store_true")
argparser.add_argument("-p", "--pretty-print", help = "pretty print generated output", action = "store_true")
argparser.add_argument("-s", "--seed", help = "seed for random number generator", type = int, default = 42)
argparser.add_argument("-c", "--shares", help = "approximate share of primitive, incomple information, and derived types in the records respectively", type = int, nargs = 3, default = [7, 1, 12])
argparser.add_argument("-k", "--has-key", help = "ensures that this key exists in every record", type = str, default = None)
argparser.add_argument("-i", "--add-id", help = "add numerical id field to each record", type = str, default = None)
argparser.add_argument("-l", "--key-length-range", help = "sets the range for the number of characters for the record keys", type = int, nargs = 2, default = [2, 3])
args = argparser.parse_args()

if args.has_key == "id" and args.add_key:
    argparser.error("argument --add-id already implies --has-key \"id\"")

if args.for_direct_insertion:
    adm_types.Settings.set_for_file_load(False)

random.seed(args.seed)
numpy.random.seed(int(random.getrandbits(4 * 8))) # TODO: legacy (see https://numpy.org/doc/stable/reference/random/generated/numpy.random.seed.html)

PRIMITIVE_TYPE_SHARE = args.shares[0]
INCOMPLETE_INFORMATION_TYPE_SHARE = args.shares[1]
DERIVED_TYPE_SHARE = args.shares[2]
SUM_SHARES_NON_DERIVED_TYPE = PRIMITIVE_TYPE_SHARE + INCOMPLETE_INFORMATION_TYPE_SHARE
SUM_SHARES = SUM_SHARES_NON_DERIVED_TYPE + DERIVED_TYPE_SHARE

def encapsulate_value(val: str, pretty_print: bool, key = None, id = None) -> str:
    if not key:
        key = list(id)[0] if id else None
        while key == list(id)[0] if id else None:
            key = adm_types.ADMString.generate_random_string(args.key_length_range[0], args.key_length_range[1]) # TODO: maybe set possible string lengths depending on args.num_records

    if id:
        return "{{{pp1}\"{id_key}\": {id_val},{pp2}\"{key}\": {val}{pp3}}}\n".format(key = key, val = val, pp1 = "\n" + " " * adm_types.Settings.ADM_INDENTATION if pretty_print else "", id_key = list(id)[0], id_val = id[list(id)[0]], pp2 = "\n" + " " * adm_types.Settings.ADM_INDENTATION if pretty_print else " ", pp3 = "\n" if pretty_print else "")
    else:
        return "{{{pp1}\"{key}\": {val}{pp2}}}\n".format(key = key, val = val, pp1 = "\n" + " " * adm_types.Settings.ADM_INDENTATION if pretty_print else "", pp2 = "\n" if pretty_print else "")

# https://stackoverflow.com/a/17603000
@contextlib.contextmanager
def opt_stdout_open(filename = None, mode = "w"):
    if filename:
        fd = open(filename, mode)
    else:
        fd = sys.stdout

    try:
        yield fd
    finally:
        if fd is not sys.stdout:
            fd.close()

with opt_stdout_open(args.output, "w") as output_file:
    for id in range(1, args.num_records + 1):
        type_choice = random.randint(1, SUM_SHARES)

        if type_choice <= SUM_SHARES_NON_DERIVED_TYPE:
            if PRIMITIVE_TYPE_SHARE > 0 and type_choice <= PRIMITIVE_TYPE_SHARE:
                record_val = adm_types.RandomPrimitiveTypeGenerator.generate_rand()
            else:
                record_val = adm_types.RandomIncompleteInformationTypeGenerator.generate_rand()

            record = encapsulate_value(adm_types.format(record_val, args.pretty_print), args.pretty_print, args.has_key, {args.add_id: id} if args.add_id else None)
            output_file.write(record)
        else:
            record_val = adm_types.RandomDerivedTypeGenerator.generate_rand()

            if isinstance(record_val, adm_types.ADMObject) and not args.has_key:
                if args.add_id:
                    record_val.add_key(args.add_id, id)
                output_file.write(adm_types.format(record_val, args.pretty_print) + "\n")
            else:
                record_val_str = adm_types.format(record_val, args.pretty_print)
                if args.pretty_print:
                    record_val_str = re.sub(r"\n(\s*)", r"\n{indent}\g<1>".format(indent = " " * adm_types.Settings.ADM_INDENTATION), record_val_str)

                output_file.write(encapsulate_value(record_val_str, args.pretty_print, args.has_key, {args.add_id: id} if args.add_id else None))
