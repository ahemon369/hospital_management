from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('', views.medical_record_list, name='medical_record_list'),
    path('create/', views.medical_record_create, name='medical_record_create'),
    path('<int:pk>/', views.medical_record_detail, name='medical_record_detail'),
    path('<int:pk>/update/', views.medical_record_update, name='medical_record_update'),
    path('<int:pk>/delete/', views.medical_record_delete, name='medical_record_delete'),
    path('<int:pk>/print/', views.medical_record_print, name='medical_record_print'),
]