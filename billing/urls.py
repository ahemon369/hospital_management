from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/update/', views.bill_update, name='bill_update'),
    path('<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('<int:pk>/pdf/', views.bill_pdf, name='bill_pdf'),
    path('<int:pk>/payment/', views.record_payment, name='record_payment'),
]
