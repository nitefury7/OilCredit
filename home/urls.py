from django.urls import path
import home.views as views

app_name = 'home'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
]
