from django.urls import path

from . import views

urlpatterns = [
    path('add-expense/', views.AddExpense.as_view(), name='add_expense'),
    path('edit-expense/<int:expense_id>/', views.EditExpense.as_view(), name='edit_expense'),
    path('delete-expense/<int:expense_id>/', views.DeleteExpense.as_view(), name='delete_expense'),
    path('expense-cat-sum/', views.ExpenseCategorySummaryView.as_view(), name='expense_cat_sum'),
    path('stats/', views.StatView.as_view(), name='stats'),
]
