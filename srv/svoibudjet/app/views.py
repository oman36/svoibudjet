import logging

from django.core.paginator import Paginator, EmptyPage
from django.db import models, transaction
from django.forms import model_to_dict
from django.http import Http404, JsonResponse
from django.shortcuts import render

from .check_api import API
from .models import Check, Item, QRData
from .utils import save_json, save_check

app_name = 'app'
logger = logging.getLogger('custom_debug')


def search(request):
    queryset = Check.objects.order_by('-date')
    paginator = Paginator(queryset, request.GET.get('per-page', 10))
    try:
        checks = paginator.page(request.GET.get('page', 1))
    except EmptyPage:
        raise Http404()

    return render(request, 'app/list.html', {
        'checks': checks,
        'num_pages': paginator.num_pages,
    })


def index(request):
    return render(request, 'app/index.html')


def new_check(request):
    return render(request, 'app/new_check.html')


@transaction.atomic
def add(request):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Method not allowed',
        }, status=405)

    if 'qr_code_data' not in request.POST:
        return JsonResponse({
            'message': 'Data from QR code is required',
        }, status=400)

    qr_data, created = QRData.objects.get_or_create(qr_string=request.POST['qr_code_data'])

    api = API()

    if not api.check(qr_data.qr_string):
        qr_data.is_valid = False
        qr_data.save()

        return JsonResponse({
            'message': 'Invalid check',
        }, status=406)

    qr_data.is_valid = True
    json = api.get_json(request.POST['qr_code_data'])

    if json is False:
        return JsonResponse({
            'message': 'Can not get json from api',
        }, status=406)

    data = save_json(json)

    if data is None:
        return JsonResponse({
            'message': 'Nalog api returned invalid json',
        }, status=406)

    check = save_check(data)

    qr_data.check_model = check
    qr_data.save()

    return JsonResponse({
        'message': 'ok',
        'check': model_to_dict(check),
        'items': list(Item.objects.filter(check_model=check).values())
    })
