#!/usr/bin/env python3

import random
import adm_types
import numpy
import argparse
import re



argparser = argparse.ArgumentParser()
argparser.add_argument("-n", "--num-records", help = "the number of records to be generated", type = int, required = True)
argparser.add_argument("-o", "--output", help = "output file", type = str, required = True)
argparser.add_argument("-p", "--pretty-print", help = "pretty print generated output", action = "store_true")
argparser.add_argument("-s", "--seed", help = "seed for random number generator", type = int, default = 42)
argparser.add_argument("-c", "--shares", help = "approximate share of primitive, incomple information, and derived types in the records respectively", nargs = 3, default = [7, 1, 12])
args = argparser.parse_args()

random.seed(args.seed)
numpy.random.seed(int(random.getrandbits(4 * 8))) # TODO: legacy (see https://numpy.org/doc/stable/reference/random/generated/numpy.random.seed.html)

PRIMITIVE_TYPE_SHARE = args.shares[0]
INCOMPLETE_INFORMATION_TYPE_SHARE = args.shares[1]
DERIVED_TYPE_SHARE = args.shares[2]
SUM_SHARES_NON_DERIVED_TYPE = PRIMITIVE_TYPE_SHARE + INCOMPLETE_INFORMATION_TYPE_SHARE
SUM_SHARES = SUM_SHARES_NON_DERIVED_TYPE + DERIVED_TYPE_SHARE

def encapsulate_value(val: str, pretty_print: bool) -> str:
    key = adm_types.ADMString.generate_random_string(2, 3) # TODO: maybe set possible string lengths depending on args.num_records

    return "{{{pp1}\"{key}\": {val}{pp2}}}\n".format(key = key, val = val, pp1 = "\n" + " " * adm_types.ADM_INDENTATION if pretty_print else "", pp2 = "\n" if pretty_print else "")


with open(args.output, "w") as output_file:
    for _ in range(args.num_records):
        type_choice = random.randint(1, SUM_SHARES)

        if type_choice <= SUM_SHARES_NON_DERIVED_TYPE:
            if PRIMITIVE_TYPE_SHARE > 0 and type_choice <= PRIMITIVE_TYPE_SHARE:
                record_val = adm_types.RandomPrimitiveTypeGenerator.generate_rand()
            else:
                record_val = adm_types.RandomIncompleteInformationTypeGenerator.generate_rand()

            output_file.write(encapsulate_value(adm_types.format(record_val, args.pretty_print), args.pretty_print))
        else:
            record_val = adm_types.RandomDerivedTypeGenerator.generate_rand()

            if isinstance(record_val, adm_types.ADMObject):
                output_file.write(adm_types.format(record_val, args.pretty_print) + "\n")
            else:
                record_val_str = adm_types.format(record_val, args.pretty_print)
                if args.pretty_print:
                    record_val_str = re.sub(r"\n(\s*)", r"\n{indent}\g<1>".format(indent = " " * adm_types.ADM_INDENTATION), record_val_str)

                output_file.write(encapsulate_value(record_val_str, args.pretty_print))
