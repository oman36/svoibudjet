import logging

from app.check_api import API
from app.models import QRData
from app.utils import save_check, save_json
from django.core.management.base import BaseCommand

app_name = 'app'
logger = logging.getLogger('custom_debug')


class Command(BaseCommand):
    help = 'Tries get check data from api'

    def handle(self, *args, **options):
        failed_qr_strings = QRData.objects.filter(check_model__id__isnull=True)
        api = API()
        for failed_qr_string in failed_qr_strings:
            if not failed_qr_string.is_valid:
                if not api.check(failed_qr_string.qr_string):
                    continue
                failed_qr_string.is_valid = True
                failed_qr_string.save()

            json = api.get_json(failed_qr_string.qr_string)

            if json is False:
                logger.debug('Can not get json from api by qr: %s' % failed_qr_string.qr_string)
                continue

            data = save_json(json)

            if data is None:
                logger.debug('Nalog api returned invalid json for %s' % failed_qr_string.qr_string)
                continue

            check = save_check(data)

            failed_qr_string.check_model = check
            failed_qr_string.save()
