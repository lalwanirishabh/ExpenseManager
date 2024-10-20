from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createUser, name='createUser'),
    path('<int:userId>', views.getUser, name='getUser'),
    path('delete/<int:userId>', views.deleteUser, name='deleteUser')
]