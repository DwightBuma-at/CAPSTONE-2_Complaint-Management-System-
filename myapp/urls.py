from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # http://127.0.0.1:8000/
    path('index.html', views.index_alias, name='index'),  # http://127.0.0.1:8000/index.html
    path('user.html', views.user_page, name='user'),  # http://127.0.0.1:8000/user.html
    path('admin.html', views.admin, name='admin'),
    path('admin-complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin-users/', views.admin_users, name='admin_users'),

]