from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('search-expense/', views.SearchExpenseView.as_view(), name='search_expense'),
    path('export-csv-expenses/', views.export_to_csv, name='export_to_csv'),
    path('export-excel-expenses/', views.export_to_excel, name='export_to_excel'),
    path('export-pdf-expenses/', views.export_to_pdf, name='export_to_pdf'),
]
