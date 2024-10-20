from django.urls import path
from . import views

urlpatterns=[
    path('add/', views.createExpense),
    path('user/<int:userId>', views.fetchIndividualExpense),
    
]