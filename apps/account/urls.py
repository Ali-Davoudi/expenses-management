from django.urls import path

from . import views

urlpatterns = [
    path('sign-up/', views.RegisterView.as_view(), name='register'),
    path('sign-in/', views.LoginView.as_view(), name='login'),
    path('sign-out/', views.LogoutView.as_view(), name='logout'),
    path('validate-username/', views.UsernameValidationView.as_view(), name='validate_username'),
    path('validate-email/', views.EmailValidationView.as_view(), name='validate_email'),
    path('activate/<uidb64>/<token>/', views.VerificationView.as_view(), name='verification'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('reset-password/<uidb64>/<token>', views.ResetPasswordView.as_view(), name='reset_password'),
]
