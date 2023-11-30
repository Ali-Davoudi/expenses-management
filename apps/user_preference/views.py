import os
import json

from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic.base import View
from django.contrib import messages

from .models import UserPreference


class UserPreferenceView(View):
    model = UserPreference
    template_name = 'user_preference/preference.html'
    json_file = 'currencies.json'

    def get_user_preference(self, user):
        try:
            return self.model.objects.get(user=user)
        except (self.model.DoesNotExist, TypeError):
            return None

    def get_currency_data(self):
        file_path = os.path.join(settings.BASE_DIR, self.json_file)

        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        currency_data = [{'name': k, 'value': v} for k, v in data.items()]
        return currency_data

    def get_context_data(self, user_preference=None):
        currency_data = self.get_currency_data()
        context = {
            'currency_data': currency_data,
            'user_preference': user_preference
        }
        return context

    def get(self, request):
        user_preference = self.get_user_preference(request.user)
        context = self.get_context_data(user_preference)
        return render(request, self.template_name, context)

    def post(self, request):
        user_preference = self.get_user_preference(request.user)
        currency = request.POST.get('currency')

        if currency:
            if user_preference:
                user_preference.currency = currency
                user_preference.save()
            else:
                user_preference = self.model.objects.create(user=request.user, currency=currency)

            messages.success(request, 'Changes saved')
            context = self.get_context_data(user_preference)
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'Invalid currency')
            return redirect('user_preferences')

    def dispatch(self, request, *args, **kwargs):
        if request.method not in ['GET', 'POST']:
            messages.error(request, 'Invalid request method')
            return redirect('user_preferences')

        return super().dispatch(request, *args, **kwargs)
