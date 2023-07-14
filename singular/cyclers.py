"""Cycler initializers. """

from singular import singular


def biologic() -> singular.Cycler:
    cycler = singular.Biologic
    mapper = singular.Mapper(
        time='time/s',
        voltage='Ewe/V',
        current='control/V/mA',
        capacity='Q charge/discharge/mA.h',
        cycle='half cycle'
    )
    fileformat = 'mpr'

    return cycler(mapper, fileformat)


def ivium() -> singular.Cycler:
    cycler = singular.Ivium
    mapper = singular.Mapper( 
        time='time',
        current='current',
        voltage='voltage'
    )
    fileformat = 'idf'

    return cycler(mapper, fileformat)


def neware() -> singular.Cycler:
    cycler = singular.Neware
    mapper = singular.Mapper(
        time='unix_time',
        voltage='test_vol',
        current='test_cur',
        cycle='cycle',
        capacity='test_capchg',
        dcapacity='test_capdchg'
    )
    fileformat = 'sqlite3'

    return cycler(mapper, fileformat)


def squidstat() -> singular.Cycler:
    cycler = singular.Squidstat
    mapper = singular.Mapper(
        time='UTC Time (s)',
        current='Current (A)',
        voltage='Working Electrode (V)',
        cycle='Repeats'
    )
    fileformat = 'csv'

    return cycler(mapper, fileformat)
