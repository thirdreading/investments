"""
architecture.py
"""
import os

import dask.dataframe
import numpy as np
import pandas as pd

import config
import src.cases.transactions
import src.metrics.disaggregates.structuring
import src.functions.objects


class Architecture:

    def __init__(self, storage: str):
        """

        :param storage:
        """

        # The transactions data of each segment code type is stored in s separate JSON file.  The
        # Structuring class ensures each file has the appropriate graphing structure
        self.__storage = storage
        self.__structuring = src.metrics.disaggregates.structuring.Structuring(storage=self.__storage)

        # For the menu
        self.__objects = src.functions.objects.Objects()

        # The data & fields in focus: The overall government expenditure per segment code is recorded in field <OTE>
        self.__usecols = ['code', 'OTE', 'segment_code', 'year', 'epoch']
        self.__blob = self.__read()
        self.__segment_codes = self.__blob['segment_code'].unique()

    def __read(self) -> pd.DataFrame:
        """

        :return:
        """

        # The calculations must be based on revalued data sets, hence comparable prices/costs across years.
        frame = dask.dataframe.read_csv(
            urlpath=os.path.join(config.Config().expenditure.revalued_, '*.csv'), usecols=self.__usecols)
        data = frame.compute().reset_index(drop=True)

        return data

    @dask.delayed
    def __transactions(self, segment_code: str) -> pd.DataFrame:

        # The records of a segment
        data: pd.DataFrame = self.__blob.copy().loc[self.__blob['segment_code'] == segment_code, :]

        # Per epoch year, what is each code's percentage?
        temporary = data.groupby(by=['epoch']).agg(denominator=('OTE', sum))
        data = data.copy().merge(temporary.copy(), how='left', on='epoch')
        data.loc[:, 'annual_code_%'] = 100 * data['OTE'] / data['denominator']

        return data

    @dask.delayed
    def __series(self, blob: pd.DataFrame) -> pd.DataFrame:
        """

        :param blob:
        :return:
        """

        data = blob.copy()

        # Per segment code time series, evaluate the delta percentage vis-à-vis the previous year
        data.sort_values(by=['code', 'epoch'], ascending=True, inplace=True)
        data.loc[:, 'series_delta'] = data.groupby(by=['code'])['OTE'].diff().fillna(np.NaN)
        data.loc[:, 'series_shift'] = data.groupby(by=['code'])['OTE'].shift(periods=1, fill_value=np.NaN)
        data.loc[:, 'series_delta_%'] = np.where(data['series_shift'] != 0,
                                                 100 * data['series_delta'] / data['series_shift'], np.NaN)

        return data

    @dask.delayed
    def __persist(self, blob: pd.DataFrame, segment_code: str) -> str:
        """

        :param blob:
        :param segment_code:
        :return:
        """

        return self.__structuring.exc(blob=blob, segment_code=segment_code)

    def exc(self) -> list:
        """

        :return:
        """

        computations = []
        for segment_code in self.__segment_codes:
            transactions = self.__transactions(segment_code=segment_code)
            series = self.__series(blob=transactions)
            message = self.__persist(blob=series, segment_code=segment_code)
            computations.append(message)
        dask.visualize(computations, filename='computations', format='pdf')
        messages = dask.compute(computations, scheduler='threads')[0]

        segments = src.cases.transactions.Transactions().segments
        menu = segments.rename(columns={'segment_code': 'name', 'segment_description': 'desc'})
        self.__objects.write(nodes=menu.to_dict(orient='records'), path=os.path.join(self.__storage, 'menu.json'))

        return messages
