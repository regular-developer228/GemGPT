from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('send/' ,views.send, name='send_msg'),
    path('clear/', views.clear, name='clear_hst')
]
