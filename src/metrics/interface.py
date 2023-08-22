"""
interface.py
"""
import os
import logging

import src.metrics.overall
import src.functions.objects
import src.functions.directories


class Interface:
    """

    """

    def __init__(self):
        """

        """

        self.__storage = os.path.join(os.getcwd(), 'warehouse', 'expenditure', 'metrics')
        directories = src.functions.directories.Directories()
        directories.cleanup(path=self.__storage)
        directories.create(path=self.__storage)

        # logging
        logging.basicConfig(level=logging.INFO,
                            format='\n\n%(message)s\n%(asctime)s.%(msecs)03d',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.__logger = logging.getLogger(__name__)

    @staticmethod
    def __persist(dictionary: any, path: str) -> str:
        """

        :param dictionary:
        :return:
        """

        return src.functions.objects.Objects().write(nodes=dictionary, path=path)

    def __disaggregates(self):
        pass

    def __aggregates(self) -> str:

        overall = src.metrics.overall.Overall().exc()

        parts = []
        for interest in ['annual_total', 'annual_segment_%', 'series_delta_%']:

            frame = overall[['epoch', interest, 'segment_code']]
            structure = frame.pivot(index='epoch', columns='segment_code', values=interest)
            structure.reset_index(drop=False, inplace=True)
            node = structure.to_dict(orient='tight')
            node['name'] = interest
            parts.append(node)

        return self.__persist(dictionary=parts, path=os.path.join(self.__storage, 'aggregates.json'))

    def exc(self):

        message = self.__aggregates()
        self.__logger.info(message)
