from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
]

htmxpatterns = [
    path('dashboard/accounts_payable_detail/', views.accounts_payable_detail, name='accounts_payable_detail'),
    path('dashboard/accounts_receivable/', views.accounts_receivable_detail, name='accounts_receivable'),
    path('dashboard/total_purchases_detail/', views.total_purchases_detail , name='total_purchases_detail'),
    path('dashboard/total_sales/',views.total_sales_detail , name='total_sales_detail'),
    path('dashboard/total_income/', views.total_income_detail, name='total_income'),
    path('dashboard/total_expenses/', views.total_expenses_detail , name='total_expenses'),
]

urlpatterns += htmxpatterns

