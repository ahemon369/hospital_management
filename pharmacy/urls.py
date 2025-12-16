from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('create/', views.medicine_create, name='medicine_create'),
    path('<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('<int:pk>/update/', views.medicine_update, name='medicine_update'),
    path('<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('<int:pk>/update-stock/', views.update_stock, name='update_stock'),
]