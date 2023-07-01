"""Stripped down version of our anyware repo (neware abstraction)."""

import sqlite3

import pandas as pd

from typing import Optional, Union

TABLE = 'test'


def _parse(fields: Union[dict[str, str], list]) -> str:
    """Parses fields to query string.

    Args:
        fields (Union[dict[str, str], list]): See get_query().

    Returns:
        str: Parsed field names ready to be passed to query string.
    """

    if isinstance(fields, list):
        return ', '.join(field for field in fields)
    
    return ', '.join(f'{key} as {val}' for key, val in fields.items())


def capacity_query() -> str:
    """Standardized query for capacity data.
    
    Returns:
        str: Query string.
    """

    return f"""
        SELECT 
            cycle, 
            test_vol AS voltage,
            MAX(test_capchg) AS capacity, 
            MAX(test_capdchg) AS dcap,
            MAX(test_capdchg) / MAX(test_capchg) AS ce
        FROM 
            {TABLE}
        GROUP BY 
            cycle
        """


def load(path, query: str, time_col: str = 'time') -> pd.DataFrame:
    """Wrapper for fetching anyware data.
    
    Args:
        query_ (str): Query string.
    
    Returns:
        pd.DataFrame: Dataframe of queried data.

    Raises:
        ValueError: If self.paths is not defined.
    """

    connection = sqlite3.connect(path)

    echem: pd.DataFrame = pd.read_sql(
        con=connection,
        sql=query
    )

    try:
        echem.set_index(time_col, inplace=True)
    except KeyError:
        pass

    return echem


def parse_query(fields: Optional[Union[dict[str, str], list[str]]] = None, subsampling_factor: Optional[int] = None) -> str:
    """Generates query string for anyware.

    Selects columns from anyware table. Optionally subsamples.

    Args:
        fields (Union[dict[str: str], list], optional): Columns to query.
            Three cases, depending on the type passed:
            1) If fields are a dict, then keys are the column names in the database and
                values are the renamed fields. This can be useful bc some of
                the original data field names are very unintuitive and unreadable names,
                e.g. 'test_vol' for what one would normally call 'voltage' or 'V'.
            2) If fields are a list, the returned dataframe will have the same (default)
                column names.
            3) Defaults to None, in which case all fields are selected with default names.
        subsampling_factor (int, optional): Subsampling factor.
            Defaults to None.

    Returns:
        str: Query string.
    """
        

    to_select: str = '*' if fields is None else _parse(fields)
    query_ = f'''
            SELECT
                {to_select}
            FROM
                "{TABLE}"
            '''

    if subsampling_factor is not None:
        query_ += f' WHERE _id % {subsampling_factor} == 0'

    return query_
