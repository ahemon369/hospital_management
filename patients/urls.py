from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update, name='patient_update'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    
    # AJAX endpoint for quick patient creation
    path('quick-create/', views.patient_quick_create, name='patient_quick_create'),
]