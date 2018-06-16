from ...models import Check, Item, Shop, Product
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from io import BytesIO
import json
import os.path
from telegram import Bot, error
from time import sleep
import traceback


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    json_files_path = settings.BASE_DIR + '/app/checks'

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
            json_data = self.save_json(json_string)
            if not json_data:
                self.stdout.write('[%s] File not json' % update.update_id, ending='\n')
                continue

            self.save_check(json_data)
        self.stdout.write('success', ending='\n')
        sleep(1)

    def save_json(self, json_string):
        json_data = json.loads(json_string)

        if 'dateTime' not in json_data:
            return None

        if not os.path.isdir(self.json_files_path):
            os.makedirs(self.json_files_path)

        filename = str(json_data['dateTime']) + '.json'
        with open(self.json_files_path + '/' + filename, 'w+') as file:
            file.write(json_string)
        return json_data

    def get_json_string(self, update):
        byte_array = BytesIO()
        update.message.document.get_file().download(out=byte_array)
        byte_array.seek(0)

        return byte_array.read().decode('utf8')

    def save_check(self, data):
        date = datetime.fromtimestamp(data['dateTime']).isoformat()
        check = Check.objects.filter(date=date).first()
        if Check.objects.filter(date=date).first():
            self.stdout.write('Check %d exists...' % check.id, ending='\n')
            return check

        self.stdout.write('Saving %s...' % date, ending='\n')
        shop = Shop.objects.filter(inn=data['userInn']).first()
        if not shop:
            shop = Shop()
            shop.inn = data['userInn']
            shop.name = data['user'] or 'unknown'
            shop.save()

        check = Check()
        check.date = date
        check.total_sum = data['totalSum'] / 100
        check.discount = (data['discount'] or 0) / 100
        check.discount_sum = (data['discountSum'] or 0) / 100
        check.shop = shop
        check.save()

        for item in data['items']:
            self.save_item(check, item)

        print('Check %s was saved' % check)
        return check

    def save_item(self, check, item_data):
        product = Product.objects.filter(name=item_data['name'], shop=check.shop).first()
        if not product:
            product = Product()
            product.shop = check.shop
            product.name = item_data['name']
            product.save()

        item = Item()
        item.check_model = check
        item.product = product
        item.price = item_data['price'] / 100
        item.quantity = item_data['quantity']
        item.sum = item_data['sum'] / 100
        item.save()
        return item
