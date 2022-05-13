from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('place_order/', views.place_order, name='place_order'),
    path('approve_invoice/<int:id>', views.approve_invoice, name='approve_invoice'),
    path('reject_invoice/<int:id>', views.reject_invoice, name='reject_invoice'),
    path('set_credit/', views.set_credit, name='set_credit'),
]
