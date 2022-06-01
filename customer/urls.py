from django.urls import path
import customer.views as views

app_name = 'customer'

urlpatterns = [
    path('', views.Orders.as_view(), name='orders'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),

    # Graph API
    path('spendings_by_product/', views.spendings_by_product,
         name='spendings_by_product'),
    path('latest_spendings/', views.latest_spendings,
         name='latest_spendings'),
]
