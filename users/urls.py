from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createUser),
    path('<int:userId>', views.getUser),
    path('delete/<int:userId>', views.deleteUser)
]