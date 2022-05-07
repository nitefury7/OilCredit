from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('approve_invoice/<int:id>', views.approve_invoice, name='approve_invoice'),
]
