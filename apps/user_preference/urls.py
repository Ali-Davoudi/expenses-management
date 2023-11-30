from django.urls import path

from . import views

urlpatterns = [
    path('user-preferences/', views.UserPreferenceView.as_view(), name='user_preferences'),
]
