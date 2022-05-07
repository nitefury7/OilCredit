from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
