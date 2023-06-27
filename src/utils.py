import os
from typing import Union

from dotenv import dotenv_values
import numpy as np
import pandas as pd


config: dict[str, str] = dotenv_values('.env')
base_directory: str = config['base_directory']


def find_experiment(filename: str) -> Union[str, None]:
    for root, _, files in os.walk(base_directory):
        if filename not in files:
            continue
        
        return os.path.join(root, filename)
    
def fix_cycle(timeseries: pd.DataFrame, column: str = 'current', threshold: float = 0.001) -> None:
    '''The raw anyware data doesn't have the typical cycle number in the case
    of anything more complicated than CC/CC.
    
    Neware is stupid.
    
    Args:
        timeseries (pd.DataFrame): Electrochemical data as received from anyware.
        column (str, optional): The column to detect changes on.
            Defaults to 'current'.
        threshold (float, optional): The threshold upon which we assume cycle is changing.
            Defaults to 0.001.
    '''
    
    difference = timeseries.diff()
    boolean = np.array(difference[column] > threshold)
    # //2 bc we are only interested in cycle changes, not step changes from OCP to CC
    timeseries['cycle'] = np.cumsum(boolean) // 2 
