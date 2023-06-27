##Author: Gunnar
##Date Started: 2023-06-26
##Notes: Unified interface for loading any electrochemical timeseries.
##Assumes non-neware data resides in labdaq. Just call load(id_).

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

from galvani import BioLogic
import numpy as np
import pandas as pd

from src.anyware import Anyware
import src.utils as utils


@dataclass
class Mapper:
    """Map original field names to standardized column names."""
    
    time: str
    voltage: str
    current: str
    cycle: str = None

    capacity: Optional[str] = None
    dcapacity: Optional[str] = None

    def flip(self) -> dict[str, str]:
        """Flip key-value pairs."""
        return dict([(value, key) for key, value in self.__dict__.items()])


class Cycler(ABC):
    """"""
    def __init__(self, mapper: Optional[Mapper] = None, fileformat: Optional[str] = None):
        self.mapper: Mapper = mapper
        self.fileformat: str = fileformat
        self._timeseries: pd.DataFrame = None

    @property
    def timeseries(self) -> pd.DataFrame:
        return self._timeseries

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def parse(self) -> None:
        pass

    def _parse(self) -> None:
        columns: dict[str, str] = self.mapper.flip()
        self._timeseries = self._timeseries.filter(items=columns.keys())
        self._timeseries.rename(columns=columns, inplace=True)
        self._timeseries.set_index('time', inplace=True)


class Biologic(Cycler):
    def load(self, path):
        mpr_file = BioLogic.MPRfile(path)
        self._timeseries = pd.DataFrame(mpr_file.data)
        
    def parse(self):
        self._parse()
        self._timeseries['cycle'] //= 2
        self._timeseries['dcapacity'] = self._timeseries['capacity'].apply(lambda x: x if x < 0 else 0)  # Lambda is the most unreadable stuff ever, but is reasonably readable here
        self._timeseries['capacity'] = self._timeseries['capacity'].apply(lambda x: x if x > 0 else 0)


class Ivium(Cycler):
    def load(self, path):
        """Credit to Andrew Wang."""
        
        self.raw_data = open(
            path,
            encoding="latin-1"
        ).read().split("primary_data")[1].split("osc_data")[0].split("\n")
        
    def parse(self):
        rows = []

        for candidate_row in self.raw_data:
            if np.size(candidate_row.split()) != 3:
                continue
            
            if candidate_row.find('=') != -1:
                continue

            row = np.array(candidate_row.split()).astype(float)
            rows.append(row)

        self._timeseries = pd.DataFrame(
            data=rows,
            columns=("time", "current", "voltage")
        )
        self._timeseries.set_index('time', inplace=True)

        fix_cycle(self._timeseries)


class Neware(Cycler):
    def load(self, id_):
        self.anyware = Anyware()
        self.anyware.set_paths(id_=id_)
        query = self.anyware.get_query(fields=self.mapper.flip())        
        self._timeseries = self.anyware.get(query=query)

    def parse(self):
        self.anyware.fix_cycle(self._timeseries)


class Squidstat(Cycler):
    def load(self, path):
        self._timeseries = pd.read_csv(path)

    def parse(self):
        self._parse()


def find_cycler(cyclers: Tuple[Cycler, ...], id_: str) -> Tuple[Cycler, str]:
    for cycler in cyclers:
        filename = f'{id_}.{cycler.fileformat}'
        path = utils.find_experiment(filename)

        if path is not None:
            break

    if path is None:
        path = id_
        cycler = neware

    return cycler, path