from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),  # URL name used in the redirect
]
