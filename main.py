from typing import Tuple

import pandas as pd

import src.singular as singular

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


def load(id_: str) -> pd.DataFrame:
    cycler, path = singular.find_cycler(cyclers=cyclers, id_=id_)
    cycler.load(path)
    cycler.parse()

    return cycler.timeseries

        
def main():
    """For testing purposes"""
    
    dummy_ids = {
        'ivium': '20210621_c10x3_c3_acoustics60',
        'squidstat': '1_AP_Si_Formation_EIS-Open Circuit Potential 20230623 175329',
        'biologic': 'KS_2023_05_16_cont',
        'neware': 'GM_GT_FR2_2023_05_04_1'
    }

    for dummy_id in dummy_ids.values():
        echem = load(id_=dummy_id)
        print(echem.info())


if __name__ == '__main__':
    main()