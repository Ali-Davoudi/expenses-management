from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.account.urls')),
    path('', include('apps.expense.urls')),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.user_preference.urls')),
]
