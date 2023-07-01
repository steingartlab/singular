import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

with open('config.json', 'r') as file:
    config = json.load(file)

base_directory: str = config['base_directory']


def find_experiment(filename: str) -> Path:
    """Searches recursively for file with name that matches.

    Args:
        filename (str): Experiment ID + file ending.

    Raises:
        FileNotFoundError: If no file with filename is found.

    Returns:
        Path: To file containing experiment.
    """


    for root, _, files in os.walk(base_directory):

        if filename not in files:
            continue

        return Path(root, filename)
    
    raise FileNotFoundError(f'No filename matches the id_ {filename}.')
    

def fix_cycle(timeseries: pd.DataFrame, column: str = 'current', threshold: float = 1e-3) -> None:
    '''The raw anyware data doesn't have the typical cycle number in the case
    of anything more complicated than CC/CC.
    
    This fixes it in the case of alternating CC/OCV steps. Not perfect, but good enough
    for all of my applications!
    
    Args:
        timeseries (pd.DataFrame): Electrochemical data as received from anyware.
        column (str, optional): The column to detect changes on.
            Defaults to 'current'.
        threshold (float, optional): The threshold upon which we assume cycle is changing.
            Defaults to 1e-3.
    '''
    
    difference = timeseries.diff()
    boolean = np.array(difference[column] > threshold)
    # //2 bc we are only interested in cycle changes, not step changes from OCP to CC
    timeseries['cycle'] = np.cumsum(boolean) // 2 
