from django.urls import path
import member.views as views

app_name = 'member'

urlpatterns = [
    path('', views.Orders.as_view(), name='orders'),
    path('spendings_by_product/', views.spendings_by_product, name='spendings_by_product'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('cancel_order/<int:id>', views.cancel_order, name='cancel_order'),
]
