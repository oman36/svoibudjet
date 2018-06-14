from ...models import Check, Item, Shop, Product
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from io import BytesIO
import json
from telegram import Bot
from time import sleep


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    json_files_path = settings.BASE_DIR + '/app/checks'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Start", ending='\n')
        bot = Bot('563615406:AAHG19VLOXuvfKIbbtlCjWmvp_zP64UzTPQ')
        print(bot.getMe())
        while True:
            for update in bot.getUpdates():
                try:
                    update.message.document
                except (KeyError, AttributeError):
                    continue
                if not update.message.document:
                    continue
                self.save_check(self.save_json(self.get_json_string(update)))
            sleep(1)

    def save_json(self, json_string):
        json_data = json.loads(json_string)
        with open('/'.join((self.json_files_path, str(json_data['dateTime']) + '.json')), 'w+') as file:
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
            return check
        print('Saving %s...' % date)
        shop = Shop.objects.filter(inn=data['userInn']).first()
        if not shop:
            shop = Shop()
            shop.inn = data['userInn']
            shop.name = data['user']
            shop.save()

        check = Check()
        check.date = date
        check.total_sum = data['totalSum']
        check.discount = data['discount'] or 0
        check.discount_sum = data['discountSum'] or 0
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
