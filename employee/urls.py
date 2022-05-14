from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.Dashboard.as_view(), name='dashboard'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('place_order/', views.PlaceOrder.as_view(), name='place_order'),
    path('approve_invoice/<int:id>', views.approve_invoice, name='approve_invoice'),
    path('reject_invoice/<int:id>', views.reject_invoice, name='reject_invoice'),
    path('set_credit/', views.SetCredit.as_view(), name='set_credit'),
]
