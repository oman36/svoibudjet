import logging

from django.core.paginator import Paginator, EmptyPage
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
        'checks'   : checks,
        'num_pages': paginator.num_pages,
    })


def index(request):
    return render(request, 'app/index.html')


def new_check(request):
    qr_data_list = QRData.objects\
        .values('id', 'check_model__id', 'qr_string', 'created_at', 'is_valid')\
        .order_by('-created_at')[:10]

    return render(request, 'app/new_check.html', {
        'qr_data_list': qr_data_list,
    })


def get_qr_data_list(request):
    qr_data_list = QRData.objects\
        .values('id', 'check_model__id', 'qr_string', 'created_at', 'is_valid')\
        .order_by('-created_at')[:10]

    return render(request, 'app/parts/qr_data_list.html', {
        'qr_data_list': qr_data_list,
    })


def add(request):
    if request.method != 'POST':
        return JsonResponse({
            'message': 'Method not allowed',
        }, status=405)

    if 'qr_code_data' not in request.POST or not request.POST['qr_code_data'].strip():
        return JsonResponse({
            'message': 'Data from QR code is required',
        }, status=400)

    qr_data, created = QRData.objects.get_or_create(qr_string=request.POST['qr_code_data'].strip())

    api = API()

    if not api.check(qr_data.qr_string):
        qr_data.is_valid = False
        qr_data.save()

        return JsonResponse({
            'message': 'Invalid check',
        }, status=406)

    qr_data.is_valid = True
    json = api.get_json(qr_data.qr_string)

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
        'check'  : model_to_dict(check),
        'items'  : list(Item.objects.filter(check_model=check).values())
    })


def qr_strings(request):
    queryset = QRData.objects.order_by('-created_at')

    if request.GET.get('failed_only', False):
        queryset = queryset.filter(check_model_id__isnull=True)
    elif request.GET.get('invalid_only', False):
        queryset = queryset.filter(is_valid=False)

    paginator = Paginator(queryset, request.GET.get('per-page', 10))
    try:
        strings = paginator.page(request.GET.get('page', 1))
    except EmptyPage:
        raise Http404()

    return render(request, 'app/qr_strings.html', {
        'strings'   : strings,
        'num_pages': paginator.num_pages,
        'repr': repr(request.resolver_match),
    })


def delete_qr_string(request, model_id):
    try:
        string = QRData.objects.get(id=model_id)
    except QRData.DoesNotExist:
        raise Http404()

    string.delete()

    return JsonResponse({
        'success': True,
    })


def update_qr_string(request, model_id):
    try:
        string = QRData.objects.get(id=model_id)
    except QRData.DoesNotExist:
        raise Http404()

    if 'qr_string' not in request.POST or not request.POST['qr_string'].strip():
        return JsonResponse({
            'message': 'qr_string is required',
        }, status=400)

    string.qr_string = request.POST['qr_string'].strip()

    if QRData.objects.filter(qr_string=string.qr_string).exists():
        return JsonResponse({
            'message': 'qr_string "%s" already exist' % string.qr_string,
        }, status=400)

    string.save()

    return JsonResponse({
        'success': True,
    })