from django.shortcuts import render
from .models import Check

app_name = 'app'


def index(request):
    checks = Check.objects.order_by('-date')
    total = 0
    for check in checks:
        total += check.total_sum

    return render(request, 'app/index.html', {
        'checks': checks,
        'total': total
    })
