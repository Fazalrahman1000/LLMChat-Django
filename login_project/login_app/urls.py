from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("chat_pate/", views.login_view, name="blank_page"),
]
