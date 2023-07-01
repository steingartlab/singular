from pathlib import Path
from typing import Callable, Tuple

import pandas as pd

from singular import singular, utils


def biologic() -> singular.Cycler:
    mapper = singular.Mapper(
        time='time/s',
        voltage='Ewe/V',
        current='control/V/mA',
        capacity='Q charge/discharge/mA.h',
        cycle='half cycle'
    )

    return singular.Biologic(mapper=mapper, fileformat='mpr')


def ivium() -> singular.Cycler:
    mapper = singular.Mapper( 
        time='time',
        current='current',
        voltage='voltage'
    )

    return singular.Ivium(mapper=mapper, fileformat='idf')


def neware() -> singular.Cycler:
    mapper = singular.Mapper(
        time='unix_time',
        voltage='test_vol',
        current='test_cur',
        cycle='cycle',
        capacity='test_capchg',
        dcapacity='test_capdchg'
    )

    return singular.Neware(mapper=mapper, fileformat='sqlite3')


def squidstat() -> singular.Cycler:
    mapper = singular.Mapper(
        time='UTC Time (s)',
        current='Current (A)',
        voltage='Working Electrode (V)',
        cycle='Repeats'
    )
    
    return singular.Squidstat(mapper, fileformat='csv')


def initialize(initializers: tuple[Callable[[], singular.Cycler], ...]) -> list[singular.Cycler]:
    cyclers = list()

    for initializer in initializers:
        cyclers.append(initializer())

    return cyclers


def match_cycler(cyclers: tuple[Callable[[], singular.Cycler], ...], id_: str) -> Tuple[singular.Cycler, Path]:

    for cycler in cyclers:
        filename: str = f'{id_}.{cycler.fileformat}'

        try:
            path: Path = utils.find_experiment(filename)
            break
        except FileNotFoundError:
            continue

    if 'path' not in locals():
        raise FileNotFoundError(
            f'No filename matches the id_ {id_}. Are you sure the filename is correct?'
        )

    return cycler, path


def load(id_: str) -> pd.DataFrame:

    initializers: tuple[Callable[[], singular.Cycler], ...] = (
        biologic,
        ivium,
        neware,
        squidstat
    )
    cyclers: Tuple[singular.Cycler, ...] = initialize(initializers)

    cycler, path = match_cycler(cyclers=cyclers, id_=id_)
    cycler.load(path)
    cycler.parse()

    return cycler.timeseries