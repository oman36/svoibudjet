import requests
from urllib.parse import parse_qs

from django.conf import settings


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
        query = {k: v[0] for k, v in parse_qs(query_str).items()}

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
        query = {k: v[0] for k, v in parse_qs(query_str).items()}

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

        import logging
        import datetime
        logger = logging.Logger('f')
        logger.handlers.append(logging.FileHandler('debug.log'))
        def log(*msg):
            for m in msg:
                logger.debug('[%s] %s' % (datetime.datetime.isoformat(datetime.datetime.now()), repr(m)))
        log(self.__build_url(uri) + '?' +  '&'.join([str(key) + '=' + str(val) for key, val in params.items()]))
        return response.status_code == 204


    def __build_url(self, uri):
        return self.endpoint + (uri[1:] if uri[:1] == '/' else uri)
