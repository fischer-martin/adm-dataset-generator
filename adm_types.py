import random
import re
import json
import numpy
import math
import string
import datetime
import calendar
import uuid

REMOVE_QUOTE_ESCAPE_MARKER = '😃'
SET_QUOTE_ESCAPE_MARKER = '♡'
REPLACE_MULTISET_BRACES_ESCAPE_MARKER = '😘'

class ADMJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if getattr(o, "__module__") == __name__:
            return o.toADM()
        else:
            return json.JSONEncoder.default(self, o)

# formats an ADM instance into a string that represents it
def format(adm: object, pretty_print = False) -> str:
    adm_string = json.dumps(adm, cls = ADMJSONEncoder, indent = 4 if pretty_print else None, ensure_ascii = False)
    adm_string = re.sub(r"\"{re}|{re}\"".format(re = REMOVE_QUOTE_ESCAPE_MARKER), "", adm_string)
    # does this already make me a regex wizard apprentice?
    # grouping syntax: https://stackoverflow.com/a/5984688
    adm_string = re.sub(r"\[\s*\"{re}\",(( )?|(\n)?)".format(re = REPLACE_MULTISET_BRACES_ESCAPE_MARKER), r"{{\g<3>", adm_string)
    adm_string = re.sub(r",\s*\"{re}\"(\s*)\]".format(re = REPLACE_MULTISET_BRACES_ESCAPE_MARKER), r"\g<1>}}", adm_string)
    adm_string = adm_string.replace(SET_QUOTE_ESCAPE_MARKER, '"')

    return adm_string

class ADMArgumentException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ADMEscapeMarkerException(ADMArgumentException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    @staticmethod
    def check_alphabet(alphabet: list):
        escape_markers = [REMOVE_QUOTE_ESCAPE_MARKER, SET_QUOTE_ESCAPE_MARKER, REPLACE_MULTISET_BRACES_ESCAPE_MARKER]

        for symbol in alphabet:
            for escape_marker in escape_markers:
                if escape_marker in symbol:
                    raise ADMEscapeMarkerException("symbol '{symbol}' in alphabet contains the escape marker {escape_marker}".format(symbol = symbol, escape_marker = escape_marker))
        


class ADMBoolean:
    val: bool

    def __init__(self, val: bool):
        self.val = val

    def toADM(self) -> bool:
        return self.val

    @staticmethod
    def generate_rand():
        # https://stackoverflow.com/a/6824868
        return ADMBoolean(bool(random.getrandbits(1)))

class ADMString:
    val: str

    def __init__(self, val: str):
        self.val = val

    def toADM(self) -> str:
        return self.val

    @staticmethod
    def generate_rand(length = 5, alphabet = list(string.ascii_lowercase)):
        ADMEscapeMarkerException.check_alphabet(alphabet)

        rand_string = ""
        for _ in range(length):
            rand_string += str(alphabet[random.randrange(0, len(alphabet))])

        return ADMString(rand_string)

class AbstractADMNumberBaseType:
    min_val = 0
    max_val = 0
    type_specifier = None

    def __init__(self, val):
        self.check_range(val)
        self.val = val

    def check_range(self, val):
        if val < self.min_val or val > self.max_val:
            raise ADMArgumentException("{val} is too large for this data type (min: {min_val}, max: {max_val})".format(val = val, min_val = self.min_val, max_val = self.max_val))

    def toADM(self):
        if self.type_specifier:
            return "{remq}{type_specifier}({setq}{val}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, type_specifier = self.type_specifier, val = self.val)
        else:
            return self.val

class ADMTinyInt(AbstractADMNumberBaseType):
    min_val = -128
    max_val = 127
    type_specifier = "tiny"

    @staticmethod
    def generate_rand():
        return ADMTinyInt(random.randint(ADMTinyInt.min_val, ADMTinyInt.max_val))

class ADMSmallInt(AbstractADMNumberBaseType):
    min_val = -32768
    max_val = 32767
    type_specifier = "smallint"

    @staticmethod
    def generate_rand():
        return ADMSmallInt(random.randint(ADMSmallInt.min_val, ADMSmallInt.max_val))

class ADMInt(AbstractADMNumberBaseType):
    min_val = -2147483648
    max_val = 2147483647

    @staticmethod
    def generate_rand():
        return ADMInt(random.randint(ADMInt.min_val, ADMInt.max_val))

class ADMBigInt(AbstractADMNumberBaseType):
    min_val = -9223372036854775808
    max_val = 9223372036854775807
    type_specifier = "bigint"

    @staticmethod
    def generate_rand():
        return ADMBigInt(random.randint(ADMBigInt.min_val, ADMBigInt.max_val))

class AbstractADMFloatingPointBaseType(AbstractADMNumberBaseType):
    special_values = [math.nan, math.inf, -math.inf]

    def check_range(self, val):
        if val not in self.special_values:
            super().check_range(val)

    def toADM(self):
        if self.val not in self.special_values:
            value = self.val
        elif math.isnan(self.val):
            value = "NaN"
        else:
            # inf or -inf
            value = str(self.val).upper()

        return "{remq}{type_specifier}({setq}{val}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, type_specifier = self.type_specifier, val = value)

    @staticmethod
    def generate_rand_special_value() -> float:
        return AbstractADMFloatingPointBaseType.special_values[random.randrange(0, len(AbstractADMFloatingPointBaseType.special_values))]

class ADMFloat(AbstractADMFloatingPointBaseType):
    min_val = numpy.finfo(numpy.float32).min
    max_val = numpy.finfo(numpy.float32).max
    type_specifier = "float"

    @staticmethod
    def random_float():
        return numpy.random.uniform(ADMFloat.min_val, ADMFloat.max_val)

    @staticmethod
    def generate_rand(special_value = False):
        if special_value:
            return ADMFloat(AbstractADMFloatingPointBaseType.generate_rand_special_value())
        else:
            # numpy-random.uniform(a, b) only draws from [a, b) but
            # I guess that's ok since we don't really rely on the value
            return ADMFloat(ADMFloat.random_float())

class ADMDouble(AbstractADMFloatingPointBaseType):
    min_val = numpy.finfo(numpy.float64).min
    max_val = numpy.finfo(numpy.float64).max
    type_specifier = "double"

    @staticmethod
    def random_double():
        #return numpy.random.uniform(ADMDouble.min_val, ADMDouble.max_val)
        return ADMFloat.random_float() # TODO: double boundaries cause overflow

    @staticmethod
    def generate_rand(special_value = False):
        if special_value:
            return ADMDouble(AbstractADMFloatingPointBaseType.generate_rand_special_value())
        else:
            # numpy-random.uniform(a, b) only draws from [a, b) but
            # I guess that's ok since we don't really rely on the value
            return ADMDouble(ADMDouble.random_double())

class ADMBinary:
    hex_digits = list("0123456789ABCDEF")
    val: str
    is_hex: bool

    def __init__(self, val, is_hex = True):
        self.val = val
        self.is_hex = is_hex

    def toADM(self):
        return "{remq}{type}({setq}{val}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, type = "hex" if self.is_hex else "base64", val = self.val)

    @staticmethod
    def generate_rand(num_bytes = 20):
        value = ""
        for _ in range(num_bytes * 2): # 2 digits per byte
            value += str(ADMBinary.hex_digits[random.randrange(0, len(ADMBinary.hex_digits))])

        return ADMBinary(value)

class ADMPoint:
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def toADM(self) -> str:
        return "{remq}point({setq}{x}, {y}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, x = self.x, y = self.y)

    @staticmethod
    def generate_rand():
        return ADMPoint(ADMDouble.random_double(), ADMDouble.random_double())

class ADMLine:
    x1: float
    y1: float
    x2: float
    y2: float

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def toADM(self) -> str:
        return "{remq}line({setq}{x1},{y1} {x2},{y2}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, x1 = self.x1, y1 = self.y1, x2 = self.x2, y2 = self.y2)

    @staticmethod
    def generate_rand():
        return ADMLine(ADMDouble.random_double(), ADMDouble.random_double(), ADMDouble.random_double(), ADMDouble.random_double())

class ADMRectangle:
    x1: float
    y1: float
    x2: float
    y2: float

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def toADM(self) -> str:
        return "{remq}rectangle({setq}{x1},{y1} {x2},{y2}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, x1 = self.x1, y1 = self.y1, x2 = self.x2, y2 = self.y2)

    @staticmethod
    def generate_rand():
        return ADMLine(ADMDouble.random_double(), ADMDouble.random_double(), ADMDouble.random_double(), ADMDouble.random_double())

class ADMCircle:
    x: float
    y: float
    radius: float

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
    
    def toADM(self) -> str:
        return "{remq}circle({setq}{x},{y} {radius}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, x = self.x, y = self.y, radius = self.radius)

    @staticmethod
    def generate_rand():
        return ADMCircle(ADMDouble.random_double(), ADMDouble.random_double(), ADMDouble.random_double())

class ADMPolygon:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values

    def toADM(self) -> str:
        format_string = "{remq}polygon({setq}" + str(self.x_values[0]) + "," + str(self.y_values[0])
        for i in range(1, len(self.x_values)):
            format_string += " " + str(self.x_values[i]) + "," + str(self.y_values[i])
        format_string += "{setq}){remq}"

        return format_string.format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER)

    @staticmethod
    def generate_rand(points = 6):
        x_values = []
        y_values = []
        
        for _ in range(points):
            x_values.append(ADMDouble.random_double())
            y_values.append(ADMDouble.random_double())

        return ADMPolygon(x_values, y_values)

class ADMDate:
    def __init__(self, year, month, day):
        self.val = datetime.date(year, month, day)

    def toADM(self) -> str:
        return self.val.strftime("{remq}date({setq}%Y-%m-%d{setq}){remq}").format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER)

    @staticmethod
    def generate_rand():
        year = random.randint(datetime.MINYEAR, datetime.MAXYEAR)
        month = random.randint(1, 12)
        day = random.randint(1, calendar.monthrange(year, month)[1])

        return ADMDate(year, month, day)

class ADMTime:
    # For our use case, I think it's ok if we ignore ms and timezone info.
    def __init__(self, hours, minutes, seconds):
        self.val = datetime.time(hours, minutes, seconds)

    def toADM(self) -> str:
        return self.val.strftime("{remq}time({setq}%H:%M:%S{setq}){remq}").format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER)

    @staticmethod
    def generate_rand():
        return ADMTime(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))

class ADMDateTime:
    # For our use case, I think it's ok if we ignore ms and timezone info.
    def __init__(self, years, months, days, hours, minutes, seconds):
        self.val = datetime.datetime(years, months, days, hours, minutes, seconds)

    def toADM(self) -> str:
        return self.val.strftime("{remq}datetime({setq}%Y-%m-%dT%H:%M:%S{setq}){remq}").format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER)

    @staticmethod
    def generate_rand():
        year = random.randint(datetime.MINYEAR, datetime.MAXYEAR)
        month = random.randint(1, 12)
        day = random.randint(1, calendar.monthrange(year, month)[1])

        return ADMDateTime(year, month, day, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))

class ADMDuration:
    # For our use case, I think it's ok if we ignore ms.
    def __init__(self, years, months, days, hours, minutes, seconds):
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def toADM(self) -> str:
        return "{remq}duration({setq}P{years}Y{months}M{days}DT{hours}H{minutes}M{seconds}S{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, years = self.years, months = self.months, days = self.days, hours = self.hours, minutes = self.minutes, seconds = self.seconds)

    @staticmethod
    def generate_rand():
        return ADMDuration(random.randint(1, 99), random.randint(1, 99), random.randint(1, 9999), random.randint(1, 9999), random.randint(1, 9999), random.randint(1, 9999))

class ADMYearMonthDuration:
    def __init__(self, years, months):
        self.years = years
        self.months = months

    def toADM(self) -> str:
        return "{remq}year_month_duration({setq}P{years}Y{months}M{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, years = self.years, months = self.months)

    @staticmethod
    def generate_rand():
        return ADMYearMonthDuration(random.randint(1, 99), random.randint(1, 99))

class ADMDayTimeDuration:
    # For our use case, I think it's ok if we ignore ms.
    def __init__(self, days, hours, minutes, seconds):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def toADM(self) -> str:
        return "{remq}day_time_duration({setq}P{days}DT{hours}H{minutes}M{seconds}S{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, days = self.days, hours = self.hours, minutes = self.minutes, seconds = self.seconds)

    @staticmethod
    def generate_rand():
        return ADMDayTimeDuration(random.randint(1, 9999), random.randint(1, 9999), random.randint(1, 9999), random.randint(1, 9999))

class ADMInterval:
    # We just use datetime for simplicity
    def __init__(self, datetime1: ADMDateTime, datetime2: ADMDateTime):
        self.datetime1 = datetime1
        self.datetime2 = datetime2

    def toADM(self) -> str:
        return "{remq}interval({dt1}, {dt2}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, dt1 = self.datetime1.toADM().replace(REMOVE_QUOTE_ESCAPE_MARKER, ""), dt2 = self.datetime2.toADM().replace(REMOVE_QUOTE_ESCAPE_MARKER, ""))

    @staticmethod
    def generate_rand():
        return ADMInterval(ADMDateTime.generate_rand(), ADMDateTime.generate_rand())

class ADMUUID:
    def __init__(self, uuid):
        self.uuid = uuid

    def toADM(self) -> str:
        return "{remq}uuid({setq}{uuid}{setq}){remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, setq = SET_QUOTE_ESCAPE_MARKER, uuid = self.uuid)

    @staticmethod
    def generate_reproducible_uuid() -> str:
        return str(uuid.UUID(int = random.getrandbits(128)))

    @staticmethod
    def generate_rand():
        return ADMUUID(ADMUUID.generate_reproducible_uuid())

class ADMNull:
    val = None

    def toADM(self) -> None:
        return self.val

    @staticmethod
    def generate_rand():
        return ADMNull()

class ADMMissing:
    val = "missing"

    def toADM(self) -> str:
        return "{remq}{val}{remq}".format(remq = REMOVE_QUOTE_ESCAPE_MARKER, val = self.val)

    @staticmethod
    def generate_rand():
        return ADMMissing()

class AbstractADMDerivedType:
    def __init__(self, val):
        self.val = val

class ADMObject(AbstractADMDerivedType):
    def toADM(self):
        return self.val

    @staticmethod
    def generate_rand():
        # TODO
        pass

class ADMArray(AbstractADMDerivedType):
    def toADM(self):
        return self.val

    @staticmethod
    def generate_rand():
        # TODO
        pass

class ADMMultiset(AbstractADMDerivedType):
    def toADM(self, indent = None):
        # small hack because returning a string would be way more complicated when it comes to formatting and escaping
        # now, when we already have a json string of everything, we can just convert every array
        # [ str(REPLACE_MULTISET_BRACES_ESCAPE_MARKER), a, ..., z, str(REPLACE_MULTISET_BRACES_ESCAPE_MARKER) ] into {{ a, ..., z }}
        copy = self.val.copy()
        copy.insert(0, str(REPLACE_MULTISET_BRACES_ESCAPE_MARKER))
        copy.append(str(REPLACE_MULTISET_BRACES_ESCAPE_MARKER))

        return copy

    @staticmethod
    def generate_rand():
        # TODO
        pass
