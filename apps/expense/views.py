from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum

from .models import Category, Expense


class AddExpense(View):
    template_name = 'expense/add_expense.html'
    category_model = Category
    expense_model = Expense

    def get_context_data(self):
        context = {
            'categories': self.category_model.objects.all(),
            'values': self.request.POST if self.request.method == 'POST' else None
        }
        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_context_data()

        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense_date']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, self.template_name, context)
        if not description:
            messages.error(request, 'Description is required')
            return render(request, self.template_name, context)
        if not date:
            messages.error(request, 'Date of expense is required')
            return render(request, self.template_name, context)

        self.expense_model.objects.create(user=request.user, amount=amount, description=description, category=category,
                                          date=date)
        messages.success(request, 'Your expense successfully added')
        return redirect('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.method not in ['GET', 'POST']:
            messages.error(request, 'Invalid request method')
            return redirect('add_expense')

        return super().dispatch(request, *args, **kwargs)


class EditExpense(View):
    template_name = 'expense/edit_expense.html'
    expense_model = Expense
    category_model = Category

    def get_expense(self, expense_id):
        return self.expense_model.objects.get(pk=expense_id)

    def get_caregories(self):
        return self.category_model.objects.all()

    def get_context_data(self, expense=None, category=None):
        context = {
            'expense': expense,
            'values': expense,
            'categories': category
        }
        return context

    def get(self, request, expense_id):
        expense = self.get_expense(expense_id)
        category = self.get_caregories()
        context = self.get_context_data(expense, category)
        return render(request, self.template_name, context)

    def post(self, request, expense_id):
        expense = self.get_expense(expense_id)
        category = self.get_caregories()
        context = self.get_context_data(expense, category)

        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense_date']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, self.template_name, context)
        if not description:
            messages.error(request, 'Description is required')
            return render(request, self.template_name, context)
        if not date:
            messages.error(request, 'Date of expense is required')
            return render(request, self.template_name, context)

        expense.user = request.user
        expense.amount = amount
        expense.date = date
        expense.description = description
        expense.category = category
        expense.save()

        messages.success(request, 'Your expense successfully added')
        return redirect('dashboard')

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.method not in ['POST', 'GET']:
            messages.error(request, 'Inavlid request method')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class DeleteExpense(View):
    model = Expense

    def get(self, request, expense_id):
        expense = self.model.objects.get(pk=expense_id)
        expense.delete()

        messages.info(request, f"You removed the expense ({expense.description}) successfully")
        return redirect('dashboard')


class ExpenseCategorySummaryView(View):
    model = Expense
    
    def get(self, request):
        todays_date = date.today()
        six_months_ago = todays_date - timedelta(days=30 * 6)
        expenses = self.model.objects.filter(
            user=request.user,
            date__range=(six_months_ago, todays_date)
        )
        
        category_amounts = expenses.values('category').annotate(total_amount=Sum('amount'))
        """Aggregated data (grouped): <QuerySet [{'category': 'cat_title', 'total_amount': amount}, 
           {'category': 'cat_title', 'total_amount': amount}, 
           {'category': 'cat_title', 'total_amount': amount}]>"""

        final_report = {
            category['category']: category['total_amount']
            for category in category_amounts
        }
        """{'cat_title': amount, 'cat_title': amount, 'cat_title': amount}"""
        print(final_report)

        return JsonResponse({'expense_category_data': final_report}, safe=False)


class StatView(View):
    template_name = 'expense/stats.html'
    
    def get(self, request):
        return render(request, self.template_name)
