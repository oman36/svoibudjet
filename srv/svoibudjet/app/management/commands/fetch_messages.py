import traceback
from datetime import datetime
from io import BytesIO
from time import sleep

from app.utils import save_check, save_json
from django.core.management.base import BaseCommand
from django.db import transaction
from telegram import Bot, error


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        bot = Bot('563615406:AAHG19VLOXuvfKIbbtlCjWmvp_zP64UzTPQ')

        self.stdout.write("Start", ending='\n')

        while True:
            self.fetch_messages(bot)

    @transaction.atomic
    def fetch_messages(self, bot):
        try:
            updates = bot.getUpdates(timeout=15)
        except (Exception, error.TimedOut) as ex:
            self.stdout.write('#' * 79, ending='\n')
            self.stdout.write(datetime.now().isoformat(), ending='\n')
            self.stdout.write('-' * 79, ending='\n')

            self.stdout.write(
                "An exception of type {0} occurred. Arguments:\n{2!r}. Traceback: {1}".format(
                    type(ex).__name__,
                    traceback.format_exc(),
                    ex.args
                ),
                ending='\n'
            )

            self.stdout.write('-' * 79, ending='\n')
            self.stdout.write(datetime.now().isoformat(), ending='\n')
            self.stdout.write('#' * 79, ending='\n')
            sleep(1)
            return

        self.stdout.write('count %d' % len(updates), ending='\n')
        for update in updates:
            try:
                update.message.document
            except (KeyError, AttributeError):
                self.stdout.write('[%d] Update doesn\'t have message' % update.update_id, ending='\n')
                continue

            if not update.message.document:
                self.stdout.write('[%s] Message doesn\'t have document' % update.update_id, ending='\n')
                continue

            json_string = self.get_json_string(update)
            json_data = save_json(json_string)
            if not json_data:
                self.stdout.write('[%s] File not json' % update.update_id, ending='\n')
                continue

            save_check(json_data, self.stdout)
        self.stdout.write('success', ending='\n')
        sleep(1)

    def get_json_string(self, update):
        byte_array = BytesIO()
        update.message.document.get_file().download(out=byte_array)
        byte_array.seek(0)

        return byte_array.read().decode('utf8')

