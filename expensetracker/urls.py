
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', views.BASE, name='base'),
    path('Dashboard', views.DASHBOARD, name='dashboard'),
    path('SIGNUP', views.SIGNUP, name='signup'),
    path('', views.LOGIN, name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('doLogout', views.doLogout, name='logout'),
    path('Profile', views.PROFILE, name='profile'),
    path('Profile/update', views.PROFILE_UPDATE, name='profile_update'),
    path('Password', views.CHANGE_PASSWORD, name='change_password'),
    path('AddExpenses', views.ADDEXPENSES, name='add_expenses'),
    path('ManageExpense', views.MANAGE_EXPENSES, name='manage_expense'),
    path('DeleteExpense/<str:id>', views.DELETE_EXPENSES, name='delete_expense'),
    path('data_between_dates/<int:deuser_id>/', views.data_between_dates, name='data_between_dates'),
    path('monthwise_report/<int:deuser_id>/', views.monthwise_report, name='monthwise_report'),
    path('yearwise_report/<int:deuser_id>/', views.yearwise_report, name='yearwise_report'),
    
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
