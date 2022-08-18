#!/usr/bin/env python3

import random
import adm_types
import numpy

SEED = 42

random.seed(SEED)
numpy.random.seed(int(random.getrandbits(4 * 8))) # TODO: legacy (see https://numpy.org/doc/stable/reference/random/generated/numpy.random.seed.html)

test = {
        "1": adm_types.ADMBoolean.generate_rand(),
        "2": adm_types.ADMString.generate_rand(),
        "3": adm_types.ADMTinyInt.generate_rand(),
        "4": adm_types.ADMSmallInt.generate_rand(),
        "5": adm_types.ADMInt.generate_rand(),
        "6": adm_types.ADMBigInt.generate_rand(),
        "7": adm_types.ADMFloat.generate_rand(),
        "8": adm_types.ADMFloat.generate_rand(True),
        "9": adm_types.ADMDouble.generate_rand(),
        "10": adm_types.ADMDouble.generate_rand(True),
        "11": adm_types.ADMBinary.generate_rand(),
        "12": adm_types.ADMPoint.generate_rand(),
        "13": adm_types.ADMLine.generate_rand(),
        "14": adm_types.ADMRectangle.generate_rand(),
        "15": adm_types.ADMCircle.generate_rand(),
        "16": adm_types.ADMPolygon.generate_rand(),
        "17": adm_types.ADMDate.generate_rand(),
        "18": adm_types.ADMTime.generate_rand(),
        "19": adm_types.ADMDateTime.generate_rand(),
        "20": adm_types.ADMDuration.generate_rand(),
        "21": adm_types.ADMYearMonthDuration.generate_rand(),
        "22": adm_types.ADMDayTimeDuration.generate_rand(),
        "23": adm_types.ADMInterval.generate_rand(),
        "24": adm_types.ADMUUID.generate_rand(),
        "25": adm_types.ADMNull.generate_rand(),
        "26": adm_types.ADMMissing.generate_rand(),
        "27": adm_types.ADMObject({
                "1": adm_types.ADMBoolean(False),
                "2": adm_types.ADMDouble.generate_rand(True),
                "3": adm_types.ADMObject({
                        "1": adm_types.ADMString.generate_rand()
                    }),
                "4": adm_types.ADMArray([1, "a"])
            }),
        "28": adm_types.ADMArray([
                adm_types.ADMString("test"),
                adm_types.ADMBinary.generate_rand()
            ]),
        "29": adm_types.ADMMultiset([
                adm_types.ADMMissing.generate_rand(),
                adm_types.ADMArray([
                    adm_types.ADMInt(1),
                    adm_types.ADMTinyInt(2)
                ]),
                adm_types.ADMMultiset([
                    adm_types.ADMString("a"),
                    adm_types.ADMString("b"),
                    adm_types.ADMNull()
                ]),
                adm_types.ADMMultiset([
                    adm_types.ADMPoint.generate_rand()
                    ])
                ]),
        "30": adm_types.ADMMultiset([adm_types.ADMDouble.generate_rand()])
}
print(adm_types.format(test, True))
