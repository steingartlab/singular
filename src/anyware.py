##Author: 
##Date Started:
##Notes: One-stop shop for interfacing with Anyware data.

import numpy as np
import pandas as pd
import pytz
import requests
import sqlite3
from typing import Union


from dotenv import dotenv_values

config: dict[str, str] = dotenv_values('.env')
METADATA_URL: str = config['metadata_url']

class Anyware:
    """One-stop shop for interfacing with Anyware data.

    Highlights:
    - Can both fetch data based on the 'remarks' field in the metadata and the anyware ID.
        The latter is depreciated, but kept for legacy reasons. The fact of the matter is
        that anyware IDs are software-assigned, making them hard to predict, especially for
        experiments/cells with multiple anyware IDs.
    - Flexibility in generating queries:
        1) Standardized capacity query: get_capacity_query()
        2) Semi-standardized query for a subset of fields as timeseries with optional
            subsampling: get_query(fields=fields, subsample=10)
        3) Accepts any (valid) custom-generated SQL query.
    - Automatically handles experiments with multiple anyware IDs by concatenating,
        returning a single cohesive dataframe.
    - Returns timeseries as datetime-indexed (note: not unix time) because I do be
        opinionated like that. Fork if you want it differently.
    - Can return _better_, i.e. more readable, field names using SQL mapping.

    Class Attributes:
        metadata_url (str): URL to metadata. For finding data with matching experiment ID.
        table (str): Table name. Defaults to 'test'.
        timezone (pytz.timezone): Timezone for anyware data.
            Defaults to US/Eastern.
    
    Attributes:
        paths (list[str]): List of paths to anyware data.

    Example:
        from GT_anyware import Anyware

        exp_id = 'GM_ZH_FR_2022_12_01_1'
        fields = {'unix_time': 'time', 'test_vol': 'voltage', 'test_cur': 'current', 'cycle': 'cycle'}

        anyware = Anyware()
        anyware.set_paths(id_=exp_id)
        query = anyware.get_query(fields=fields)
        data = anyware.get(query=query)
        
    """
    
    table = 'table'
    timezone = pytz.timezone('US/Eastern')

    def __init__(self):
        self.paths: list[str] = None

    @staticmethod
    def _get_anyware_ids(exp_id: str) -> list[str]:
        """Queries metadata to get anyware IDs for a given experiment ID.

        Helper function for _parse_input(). Not to be called externally.
        
        Args:
            exp_id (list[str]): Experiment ID.

        Returns:
            list[str]: List of anyware IDs.
        """

        response = requests.get(METADATA_URL, auth=('user', 'pass'))
        metadata = response.json()
        anyware_ids: list[str] = []

        for entry in metadata['data']:
            if entry[2] != exp_id:
                continue
            
            anyware_ids.append(Anyware._parse(entry[0]))

        return anyware_ids

    @staticmethod
    def _parse_input(input_: Union[str, list[str]]) -> list[str]:
        """Parses input to list of anyware IDs.

        Helper function for set_paths(). Not to be called externally.

        Args:
            input_ (Union[str, list[str]]): Input to parse.

        Returns:
            list[str]: List of anyware ID(s).
        """

        if isinstance(input_, list):
            return input_

        return [input_] if input_.count('-')==3 else Anyware._get_anyware_ids(exp_id=input_)

    @staticmethod
    def _parse(anyware_id_raw: str) -> str:
        """Parses anyware ID from raw string.

        A little hacky but whatever. Helper function for
        _generate_neware_path(). Not to be called externally.
        
        Args:
            anyware_id_raw (str): Raw string from anyware.
        
        Returns:
            str: Anyware ID.
        """

        anyware_id_wo_hyperlink = anyware_id_raw.split('inspect/')[-1]

        return anyware_id_wo_hyperlink.split("'")[0]

    @staticmethod
    def _query(path: str, query_: str) -> pd.DataFrame:
        """Queries anyware data.
        
        Helper function for get(). Not to be called externally.
        """

        connection = sqlite3.connect(path)
        data = pd.read_sql(
            con=connection,
            sql=query_
        )

        return data

    @staticmethod
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
        timeseries['cycle'] = np.cumsum(boolean) // 2  # //2 bc we are only interested in cycle changes, not step changes from OCP to CC

    @staticmethod
    def get_capacity_query() -> str:
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
                {Anyware.table}
            GROUP BY 
                cycle
            """

    @staticmethod
    def get_query(fields: Union[dict[str, str], list] = None, subsampling_factor: int = None) -> str:
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

        def parse(fields: Union[dict[str, str], list]) -> str:
            """Parses fields to query string.

            Args:
                fields (Union[dict[str, str], list]): See get_query().

            Returns:
                str: Parsed field names ready to be passed to query string.
            """

            if isinstance(fields, list):
                return ', '.join(field for field in fields)
            
            return ', '.join(f'{key} as {val}' for key, val in fields.items())
            

        to_select: str = '*' if fields is None else parse(fields)
        query_ = f'''
                SELECT
                    {to_select}
                FROM
                    "{Anyware.table}"
                '''

        if subsampling_factor is not None:
            query_ += f' WHERE _id % {subsampling_factor} == 0'

        return query_



    def set_paths(self, id_: Union[str, list[str]]) -> None:
        """Sets anyware paths from either experiment ID ('Remarks') or anyware ID.

        Historically, one would use the anyware ID URL directly, but
        that necessitates a priori knowledge of the anyware ID. It's
        simpler and more robust to use the experiment ID
        (which one should put in the 'remarks' on the neware
        software).
        
        The more severe issue with using the anyware ID directly
        is that one experiment can have multiple anyware IDs. Here
        we account for that.

        This method handles both tho—for posterity.
        
        Args:
            id_ (str): Either standard exp id, e.g. GM_GT_FR_2022_01_01_1,
                or anyware_id, e.g. 220018-1-5-509, or list of anyware IDs.
        """

        def _generate_drops_path(unit_no: str, anyware_id: str) -> str:
            return f"/drops/anyware/unit_{unit_no}/{anyware_id}.sqlite3"

        anyware_ids = Anyware._parse_input(input_=id_)

        self.paths: list[str] = []
        
        for anyware_id in anyware_ids:
            unit_no: str = anyware_id.split('-')[0]
            path: str = _generate_drops_path(unit_no=unit_no, anyware_id=anyware_id)
            self.paths.append(path)

    def get(self, query: str) -> pd.DataFrame:
        """Wrapper for fetching anyware data.
        
        Args:
            query_ (str): Query string.
        
        Returns:
            pd.DataFrame: Dataframe of queried data.

        Raises:
            ValueError: If self.paths is not defined.
        """

        if self.paths is None:
            raise NotImplementedError('Must call set_paths(exp_id) first!')

        data = pd.DataFrame()

        for path in self.paths:
            data_temporary = self._query(path=path, query_=query)
            data = pd.concat([data, data_temporary], ignore_index=True)

        time_cols = ['time', 'unix_time']

        for time_col in time_cols:
            try:
                data.set_index(time_col, inplace=True)
                return data
            except KeyError:
                continue

        return data