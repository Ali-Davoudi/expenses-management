import json
import threading

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from email_validator import validate_email, EmailNotValidError

from .utils import token_generator


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
        
    def run(self):
        self.email.send(fail_silently=False)


@method_decorator(csrf_exempt, name='dispatch')
class UsernameValidationView(View):
    model = User

    def post(self, request):
        data: dict = json.loads(request.body)
        username = data.get('username')
        user = self.model.objects.filter(username=username)

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username shoud contains Alphanumeric characters'}, status=400)
        if user.exists():
            return JsonResponse({'username_error': 'This username is already taken!'}, status=409)

        return JsonResponse({'valid_username': True})


@method_decorator(csrf_exempt, name='dispatch')
class EmailValidationView(View):
    model = User

    def post(self, request):
        data: dict = json.loads(request.body)
        email = data.get('email')
        user_email = self.model.objects.filter(email=email)

        try:
            validate_email(email)
        except EmailNotValidError:
            # When Email is not valid in terms of syntax and etc
            return JsonResponse({'invalid_email': 'Please enter a valid Email address'}, status=400)

        if user_email.exists():
            return JsonResponse({'invalid_email': 'This Email address has already been used'}, status=409)

        return JsonResponse({'valid_email': True})


class RegisterView(View):
    template_name = 'account/register.html'
    model = User

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = self.model.objects.filter(username=username, email=email)

        if not user.exists():
            if len(password) < 6:
                messages.error(request, 'Your password is too short!')
                return render(request, self.template_name, {'field_value': request.POST})

            new_user = self.model.objects.create_user(username=username, email=email)
            new_user.set_password(password)
            new_user.is_active = False
            new_user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))

            current_site = get_current_site(request)
            link = reverse('verification', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(new_user)})
            activate_url = f"http://{current_site.domain}{link}"

            email = EmailMessage(
                "Activate your account!",
                f"Hello {new_user.username}. Please use this link to activate your account\n {activate_url}",
                "adriandawoodi@gmail.com",
                [email]
            )
            # email.send(fail_silently=False)
            # Using Thread for fast email sending
            EmailThread(email).start()

            messages.success(request,
                             'Congratulations! You signed up successfully. Please visit your email inbox to activate the account')
            return render(request, self.template_name)

        return render(request, self.template_name)


class VerificationView(View):
    model = User

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.model.objects.get(id=uid)

            if not token_generator.check_token(user, token):
                # Token is invalid or expired, return a 404.
                raise Http404()

            if not user.is_active:
                user.is_active = True
                user.save()

                messages.info(request, 'Account activated successfully!')
                return redirect('login')

        except (self.model.DoesNotExist, DjangoUnicodeDecodeError):
            # Handle the case where the user does not exist (invalid UID).
            raise Http404()


class LoginView(View):
    template_name = 'account/login.html'
    model = User

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = self.model.objects.get(username=username)
            if user.is_active:
                is_correct_password = user.check_password(password)
                if is_correct_password:
                    login(request, user)
                    messages.success(request, f'Welcome {user.username}. You are now logged in')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid credentials. Try again')
                    return redirect('login')
            else:
                messages.warning(request, f'Dear {user.username}. Please first activate your account')
                return redirect('login')

        except self.model.DoesNotExist:
            messages.error(request, 'Invalid credentials. Try again')
            return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You logged out')
        return redirect('login')


class ForgetPasswordView(View):
    template_name = 'account/forget_password.html'
    model = User
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST['email']
        
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, self.template_name)
        
        user = self.model.objects.filter(email=email).first()
        
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            current_site = get_current_site(request)
            link = reverse('reset_password', kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user)})
            reset_url = f"http://{current_site.domain}{link}"

            email = EmailMessage(
                "Reset password",
                f"Hello {user.username}. Please use this link to reset your password\n {reset_url}",
                "adriandawoodi@gmail.com",
                [email]
                )
            EmailThread(email).start()
            
            messages.success(request, 'Please visit your email inbox')
            return render(request, self.template_name, {'field_value': request.POST})
        
        else:
            messages.error(request, 'Please supply a valid email')
            return render(request, self.template_name)
        

class ResetPasswordView(View):
    template_name = 'account/reset_password.html'
    model = User
    
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.model.objects.get(id=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                # Token is invalid or expired, return a 404.
                raise Http404()

        except (self.model.DoesNotExist, DjangoUnicodeDecodeError, ValueError):
            # Handle the case where the user does not exist (invalid UID).
            raise Http404()
        
        context = {
            'uidb64': uidb64,
            'token': token
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, uidb64, token):
        password = request.POST['password']
        confrim_password = request.POST['confrim-password']
        
        if password != confrim_password:
            messages.error(request, 'Passwords does not match!')
            return render(request, self.template_name)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.model.objects.get(id=uid)

            user.set_password(password)
            user.save()

            messages.success(request, 'Your password successfully changed!')
            return redirect('login')

        except Exception:
            messages.error(request, 'Something went wrong. Try again')
            return render(request, self.template_name)
