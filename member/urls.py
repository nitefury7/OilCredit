from django.urls import path
import member.views as views

app_name = 'member'

urlpatterns = [
    path('', views.orders, name='orders'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('cancel_order/<int:id>', views.cancel_order, name='cancel_order'),
]
