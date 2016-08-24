import csv

from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from exports.models import DataExport

@staff_member_required
def churn_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="churn.csv"'

    writer = csv.writer(response)
    for row in DataExport.report_churn():
        writer.writerow(row)

    return response

@staff_member_required
def mailchimp_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mailchimp.csv"'
    writer = csv.writer(response)

    header_row = DataExport.report_mailchimp_header_row()
    writer.writerow(header_row)
    for row in DataExport.report_mailchimp():
        writer.writerow(row)

    return response

@staff_member_required
def db_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="db.csv"'
    writer = csv.writer(response)
    header_row = DataExport.report_db_header_row()
    writer.writerow(header_row)
    for row in DataExport.report_db():
        writer.writerow(row)

    return response

@staff_member_required
def payments_report(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    writer = csv.writer(response)
    header_row = DataExport.report_payments_header_row()
    writer.writerow(header_row)

    for row in DataExport.report_payments():
        writer.writerow(row)

    return response
