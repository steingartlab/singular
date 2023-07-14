"""Implementation of singular.

To execute, call load(experiment_id).
"""

import inspect
from pathlib import Path
from typing import Callable, Tuple

import pandas as pd

from singular.singular import Cycler
from singular import cyclers, utils


initializer_objects = inspect.getmembers(cyclers, inspect.isfunction)
initializers: tuple[Callable[[], Cycler], ...] = tuple(
    func for _, func in initializer_objects
)
    

def initialize(
        initializers: tuple[Callable[[], Cycler], ...]) -> list[Cycler]:
    """Initialize an instance of all cycler types.

    Args:
        initializers (tuple[Callable[[], singular.Cycler], ...]): A list of cycler objects.

    Returns:
        list[singular.Cycler]: All cyclers initialized.
    """

    cyclers = list()

    for initializer in initializers:
        cyclers.append(initializer())

    return cyclers


def match_cycler(cyclers_: tuple[Callable[[], Cycler], ...], id_: str) -> Tuple[Cycler, Path]:
    """Search through directory (incl. subdirectories) for an experiment id (filename)
    and match the fileending to a cycler.

    It's a little facile bc it assumes each cycler has its own filetype. At the time of
    writing, it still holds up though. Will fix later if I add a cycler that breaks
    this pattern, but si fractum non sit, noli id reficere.

    Args:
        cyclers_ (tuple[Callable[[], singular.Cycler], ...]): All cyclers initialized.
        id_ (str): (Experiment) id. Should match filename in directory.

    Raises:
        FileNotFoundError: If file is not found!

    Returns:
        Tuple[singular.Cycler, Path]: 
    """

    for cycler in cyclers_:
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
    """Wrapper for loading experiments.
    
    Args:
        id_ (str): (Experiment) id. Should match filename in directory.

    Returns:
        pd.DataFrame: Timeseries in a standardized format.
    """

    cyclers_: Tuple[Cycler, ...] = initialize(initializers)
    cycler, path = match_cycler(cyclers_=cyclers_, id_=id_)
    cycler.load(path)
    cycler.parse()

    return cycler.timeseries