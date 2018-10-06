from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('new_check/', views.new_check, name='new_check'),
    path('add/', views.add, name='add'),
    path('get_qr_data_list/', views.get_qr_data_list, name='get_qr_data_list'),
    path('qr_strings/', views.qr_strings, name='qr_strings'),
    path('delete_qr_string/<int:model_id>/', views.delete_qr_string, name='delete_qr_string'),
    path('update_qr_string/<int:model_id>/', views.update_qr_string, name='update_qr_string'),
]
