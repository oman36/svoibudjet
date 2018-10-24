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
    path('search_products/', views.search_products, name='search_products'),
    path('category_edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('category_edit/new/', views.category_edit, name='category_new'),
    path('category_list/', views.category_list, name='category_list'),
    path('get_combined_categories/', views.get_combined_categories, name='get_combined_categories'),
    path('product/<int:product_id>/', views.product, name='product'),
]
