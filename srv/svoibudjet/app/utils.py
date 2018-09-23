import json
import logging
import os.path
import re
from datetime import datetime

from django.conf import settings

from .models import Check, Item, Shop, Product

logger = logging.getLogger('custom_debug')


def save_check(data, stdout=None):
    if isinstance(data['dateTime'], int) or re.match('^\d+$', data['dateTime']):
        date = datetime.fromtimestamp(data['dateTime']).isoformat()
    else:
        date = data['dateTime']

    check = Check.objects.filter(date=date).first()
    if Check.objects.filter(date=date).first():
        if stdout:
            stdout.write('Check %d exists...' % check.id, ending='\n')
        return check

    if stdout:
        stdout.write('Saving %s...' % date, ending='\n')
    shop = Shop.objects.filter(inn=data['userInn']).first()
    if not shop:
        shop = Shop()
        shop.inn = data['userInn']
        shop.name = data['user'] or 'unknown'
        shop.save()

    check = Check()
    check.date = date
    check.total_sum = data['totalSum'] / 100
    check.discount = data.get('discount', 0) or 0 / 100
    check.discount_sum = data.get('discountSum', 0) or 0 / 100
    check.shop = shop
    check.save()

    for item in data['items']:
        save_item(check, item)

    print('Check %s was saved' % check)
    return check


def save_item(check, item_data):
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


def save_json(json_string):
    json_files_path = settings.JSON_FILES_PATH
    json_data = json.loads(json_string)

    if 'document' in json_data:
        json_data = json_data['document']['receipt']

    if 'dateTime' not in json_data:
        logger.debug('Json data does not have dateTime: ' + str(json_string))
        return None

    if not os.path.isdir(json_files_path):
        os.makedirs(json_files_path)

    filename = str(json_data['dateTime']) + '.json'

    with open(json_files_path + '/' + filename, 'w+') as file:
        file.write(json_string)

    return json_data
