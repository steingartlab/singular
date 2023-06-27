from typing import Tuple, Union

import pandas as pd

from src import singular, utils


mapper_biologic = singular.Mapper(
    time='time/s',
    voltage='Ewe/V',
    current='control/V/mA',
    capacity='Q charge/discharge/mA.h',
    cycle='half cycle'
)
biologic = singular.Biologic(mapper=mapper_biologic, fileformat='mpr')

ivium = singular.Ivium(fileformat='idf')

mapper_neware = singular.Mapper(
    time='unix_time',
    voltage='test_vol',
    current='test_cur',
    cycle='cycle',
    capacity='test_capchg',
    dcapacity='test_capdchg'
)
neware = singular.Neware(mapper=mapper_neware)

mapper_squidstat = singular.Mapper(
    time='UTC Time (s)',
    current='Current (A)',
    voltage='Working Electrode (V)',
    cycle='Repeats'
)
squidstat = singular.Squidstat(mapper_squidstat, fileformat='csv')

cyclers: Tuple[singular.Cycler, ...] = (biologic, ivium, neware, squidstat)


def find_cycler(cyclers: Tuple[singular.Cycler, ...], id_: str) -> Tuple[singular.Cycler, str]:
    for cycler in cyclers:
        filename: str = f'{id_}.{cycler.fileformat}'
        path: Union[str, None] = utils.find_experiment(filename)

        if path is not None:
            break

    if path is None:
        path = id_
        cycler = neware

    return cycler, path


def load(id_: str) -> pd.DataFrame:
    cycler, path = find_cycler(cyclers=cyclers, id_=id_)
    cycler.load(path)
    cycler.parse()

    return cycler.timeseries