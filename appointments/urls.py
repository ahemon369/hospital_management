from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/update/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
]
