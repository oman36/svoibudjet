import logging
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import parse_qs

import requests
from django.conf import settings

logger = logging.getLogger('custom_debug')


class API:
    def __init__(self):
        self.endpoint = settings.CHECKS_API['endpoint']
        self.username = settings.CHECKS_API['username']
        self.password = settings.CHECKS_API['password']
        self.headers = {
            "Device-Id": "63343",
            "Device-OS": "Android 5.5",
            "Version": "2",
        }

    def get_json(self, query_str):
        query = self.__parse_query(query_str)
        if None is query:
            return False

        uri = 'v1/inns/*/kkts/*/fss/{fn}/tickets/{fd}'.format(fn=query['fn'], fd=query['i'])
        params = {
            'fiscalSign': query['fp'],
            'sendToEmail': "no",
        }

        tries = 0
        url = self.__build_url(uri)
        response = False

        while tries < 5:
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    auth=(self.username, self.password),
                    timeout=0.5,
                )
            except ConnectionError:
                logger.debug('Connection error')
                return False
            except TimeoutError:
                logger.debug('Timeout error')
                return False

            if response.status_code != 202:
                break

            tries += 1

        if not response.status_code != 200:
            logger.debug('Returned status code %d with massage: %s' % (response.status_code, response.text))
            return False

        return response.text

    def check(self, query_str):
        query = self.__parse_query(query_str)
        if None is query:
            return False

        uri = 'v1/ofds/*/inns/*/fss/{fn}/operations/{n}/tickets/{fd}'.format(fd=query['i'], **query)
        params = {
            'fiscalSign': query['fp'],
            'sum': int(Decimal(query['s']) * 100),
        }

        original_date = datetime.strptime(query['t'][:13], '%Y%m%dT%H%M')

        # hack. Because provider may save wrong time.
        dates_list = (
            original_date,
            original_date - timedelta(minutes=1),
            original_date + timedelta(minutes=1)
        )
        for next_date in dates_list:
            params['date'] = next_date.strftime('%Y-%m-%dT%H:%M:00')
            response = requests.get(
                self.__build_url(uri),
                params=params,
                headers=self.headers,
                auth=(self.username, self.password),
                timeout=0.5,
            )

            if response.status_code == 204:
                return True

        return False

    @staticmethod
    def __parse_query(query_str):
        query = {k: v[0] for k, v in parse_qs(query_str).items()}
        if {'i', 'fn', 't', 'fp', 's'} - set(query.keys()):
            logger.debug('invalid query_str: ' + query_str)

            return None
        return query

    def __build_url(self, uri):
        return self.endpoint + (uri[1:] if uri[:1] == '/' else uri)
