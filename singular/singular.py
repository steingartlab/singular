"""Unified interface for loading any electrochemical timeseries.
Assumes non-neware data resides in labdaq."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from galvani import BioLogic
import numpy as np
import pandas as pd

from singular import utils, anyware


@dataclass
class Mapper:
    """Map original field names to standardized column names."""
    
    time: str
    current: str
    voltage: str

    cycle: Optional[str] = None
    capacity: Optional[str] = None
    dcapacity: Optional[str] = None

    def flip(self) -> dict[str, str]:
        """Flip key-value pairs."""
        return dict([(value, key) for key, value in self.__dict__.items()])


class Cycler(ABC):
    """Base class for all cyclers, i.e. they all follow this structure."""

    def __init__(self, mapper: Mapper, fileformat: str):
        self.mapper: Mapper = mapper
        self.fileformat: str = fileformat
        self._timeseries: pd.DataFrame    

    @property
    def timeseries(self) -> pd.DataFrame:
        return self._timeseries

    @abstractmethod
    def load(self, path: Path) -> None:
        pass

    @abstractmethod
    def parse(self) -> None:
        pass

    def _parse(self) -> None:
        """Mutual parser used by >1 type of cycler."""

        columns: dict[str, str] = self.mapper.flip()
        self._timeseries = self._timeseries.filter(items=columns.keys())
        self._timeseries.rename(columns=columns, inplace=True)
        self._timeseries.set_index('time', inplace=True)


class Biologic(Cycler):
    def load(self, path):
        mpr_file = BioLogic.MPRfile(path.__str__())
        self._timeseries = pd.DataFrame(mpr_file.data)
        
    def parse(self):
        self._parse()
        self._timeseries['cycle'] //= 2
        self._timeseries['dcapacity'] = self._timeseries['capacity'].apply(
            lambda x: x if x < 0 else 0
        )
        self._timeseries['capacity'] = self._timeseries['capacity'].apply(
            lambda x: x if x > 0 else 0
        )


class Ivium(Cycler):
    """Credit to Andrew Wang."""
    
    def load(self, path):
        
        self.raw_data = open(
            path,
            encoding="latin-1"
        ).read().split("primary_data")[1].split("osc_data")[0].split("\n")
        
    def parse(self):
        rows = list()

        for candidate_row in self.raw_data:
            if np.size(candidate_row.split()) != 3:
                continue
            
            if candidate_row.find('=') != -1:
                continue

            row = np.array(candidate_row.split()).astype(float)
            rows.append(row)

        columns = [val for val in self.mapper.__dict__.values() if val is not None]
        self._timeseries = pd.DataFrame(
            data=rows,
            columns=columns
        )
        self._timeseries.set_index('time', inplace=True)

        utils.fix_cycle(self._timeseries)


class Neware(Cycler):
    """This is a stripped down version from the one we use on pithy."""

    def load(self, path):
        query: str = anyware.parse_query(self.mapper.flip())
        self._timeseries = anyware.load(path=path, query=query)

    def parse(self):
        utils.fix_cycle(self._timeseries)


class Squidstat(Cycler):
    def load(self, path):
        self._timeseries = pd.read_csv(path)

    def parse(self):
        self._parse()
