import logging
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
            'sendToEmail': "no"
        }

        response = requests.get(
            self.__build_url(uri),
            params=params,
            headers=self.headers,
            auth=(self.username, self.password)
        )

        response.raise_for_status()

        return response.text

    def check(self, query_str):
        query = self.__parse_query(query_str)
        if None is query:
            return False

        uri = 'v1/ofds/*/inns/*/fss/{fn}/operations/1/tickets/{fd}'.format(fn=query['fn'], fd=query['i'])
        date = query['t']
        params = {
            'fiscalSign': query['fp'],
            'date': '{y}-{m}-{d}T{h}:{i}:00'.format(
                y=date[:4], m=date[4:6], d=date[6:8], h=date[9:11], i=date[11:13]),
            'sum': int(float(query['s']) * 100)
        }

        response = requests.get(
            self.__build_url(uri),
            params=params,
            headers=self.headers,
            auth=(self.username, self.password)
        )

        return response.status_code == 204

    def __parse_query(self, query_str):
        query = {k: v[0] for k, v in parse_qs(query_str).items()}
        if {'i', 'fn', 't', 'fp', 's'} - set(query.keys()):
            logger.debug('invalid query_str: ' + query_str)

            return None
        return query

    def __build_url(self, uri):
        return self.endpoint + (uri[1:] if uri[:1] == '/' else uri)
