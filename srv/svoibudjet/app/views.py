from django.core.paginator import Paginator, EmptyPage
from django.forms import model_to_dict
from django.db import models, transaction
from django.http import Http404, JsonResponse
from django.shortcuts import render
from .models import Check, Item
from .check_api import API
from .utils import save_json, save_check

app_name = 'app'


def search(request):
    queryset = Check.objects.order_by('-date')
    paginator = Paginator(queryset, request.GET.get('per-page', 10))
    try:
        checks = paginator.page(request.GET.get('page', 1))
    except EmptyPage:
        raise Http404()

    return render(request, 'app/list.html', {
        'checks': checks,
        'total': queryset.aggregate(sum=models.Sum('total_sum'))['sum'],
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

    api = API()

    if not api.check(request.POST['qr_code_data']):
        return JsonResponse({
            'message': 'Invalid check',
        }, status=406)

    json = api.get_json(request.POST['qr_code_data'])

    data = save_json(json)

    check = save_check(data)

    return JsonResponse({
        'message': 'ok',
        'check': model_to_dict(check),
        'items': list(Item.objects.filter(check_model=check).values())
    })
