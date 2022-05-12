from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('place_order/', views.place_order, name='place_order'),
    path('approve_invoice/<int:id>', views.approve_invoice, name='approve_invoice'),
    path('cancel_invoice/<int:id>', views.cancel_invoice, name='cancel_invoice'),
    path('add_credit/', views.set_credit, name='add_credit'),
]
