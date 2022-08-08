from django.urls import path
import employee.views as views

app_name = 'employee'

urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('invoice_history/', views.InvoiceHistory.as_view(), name='invoice_history'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('get_customers/', views.get_customers, name='get_customers'),
    path('get_items/', views.get_items, name='get_items'),
    path('get_customer_profile/<int:id>',
         views.get_customer_profile, name='get_customer_profile'),
    path('set_credit/', views.set_credit, name='set_credit'),
]
