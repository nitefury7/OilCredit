from django.urls import path
import member.views as views

app_name = 'member'

urlpatterns = [
    path('orders/', views.orders, name='orders'),
    path('history/', views.history, name='history'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
]
