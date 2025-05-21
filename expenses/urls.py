from django.urls import path
from .views import ExpenseViewSet, ExpenseReportView


urlpatterns = [
    path('expenses/reports/', ExpenseReportView.as_view(), name='expense-reports'),
    path('expenses/', ExpenseViewSet.as_view(), name='expense'),
]