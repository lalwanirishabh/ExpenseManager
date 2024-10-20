from django.urls import path
from . import views

urlpatterns=[
    path('add/', views.createExpense, name='createExpense'),
    path('user/<int:userId>', views.fetchIndividualExpense,name='fetchIndividualExpenses'),
    path('', views.getOverallExpense,name='getOverallExpenses'),
    path('balanceSheet/<int:userId>', views.balanceSheet,name='balanceSheet')
]