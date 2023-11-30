import json
import datetime
import csv
import io
import tempfile

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

import xlsxwriter
from weasyprint import HTML

from apps.expense.models import Expense
from apps.user_preference.models import UserPreference


@method_decorator(login_required, name='dispatch')
class DashboardView(ListView):
    template_name = 'dashboard/dashboard.html'
    model = Expense
    context_object_name = 'expenses'
    paginate_by = 6
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preference'] = UserPreference.objects.filter(user=self.request.user).first()
        return context
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
    



class SearchExpenseView(View):
    model = Expense

    def post(self, request):
        search_str = json.loads(request.body).get('searchText')
        expenses = self.model.objects.filter(
            Q(amount__startswith=search_str) | Q(date__startswith=search_str) |
            Q(description__icontains=search_str) | Q(category__icontains=search_str)
        )
        data = expenses.values()
        return JsonResponse(list(data), safe=False)



def export_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses_' + str(datetime.date.today()) + '.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    
    expenses = Expense.objects.filter(user=request.user)
    
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
        
    return response


def export_to_excel(request):
    output = io.BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Get some data to write to the spreadsheet.
    data = Expense.objects.filter(user=request.user).values_list('user__username', 'category', 'description', 'amount', 'date')

    # Write titles to the Excel worksheet.
    titles = ['User','Category', 'Description', 'Amount', 'Date']
    for col_num, title in enumerate(titles):
        worksheet.write(0, col_num, title)

    # Write data below the titles.
    for row_num, columns in enumerate(data, start=1):  # Start from the second row for data
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num, col_num, cell_data)

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the HTTP response.
    filename = "Expenses_" + str(datetime.date.today()) + ".xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename

    return response


def export_to_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses_' + str(datetime.date.today()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    
    expenses = Expense.objects.filter(user=request.user)
    expenses_amounts_sum = expenses.aggregate(Sum('amount'))
    
    html_string = render_to_string('expense/expenses_pdf_output.html', {'expenses': expenses, 'total_amount': expenses_amounts_sum['amount__sum']})
    html = HTML(string=html_string)
    
    result = html.write_pdf()
    
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        
        output = open(output.name, 'rb')
        response.write(output.read())
        
    return response
