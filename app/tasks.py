import time
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app import create_app, db
from rq import get_current_job
from flask_login import current_user
from app.models import Task, Client, Download, Service, Payment
import xlsxwriter
from app import Config

app = create_app()
app.app_context().push()

filename = None


# def _set_task_progress(progress):
#     job = get_current_job()
#     if job:
#         job.meta['progress'] = progress
#         job.save_meta()
#         task = Task.query.get(job.get_id())
#         # task.user.add_notification('task_progress', {'task_id': job.get_id(),
#         #
#         #
#         #                                              'progress': progress})
#         if progress >= 100:
#             task.complete = True
#         db.session.commit()


def export_clients():
    global file_name
    try:
        job = get_current_job()
        clients = Client.query.all()
        total_clients = Client.query.count()

        # _set_task_progress(0)
        # i = 0

        file_name = 'clients' + "-" + str(time.time()) + '.xlsx'
        workbook = xlsxwriter.Workbook(Config.EXCEL_FOLDER + file_name)
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})

        worksheet = workbook.add_worksheet()

        date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0

        worksheet.write('A1', 'Name', bold)
        worksheet.write('B1', 'Email', bold)
        worksheet.write('C1', 'Contact', bold)
        worksheet.write('D1', 'Building', bold)
        worksheet.write('E1', 'House number', bold)
        worksheet.write('F1', 'Package', bold)
        worksheet.write('G1', 'Last payment date', bold)
        worksheet.write('H1', 'Due date', bold)

        worksheet.set_column('A:B', 30)
        worksheet.set_column('B:C', 30)
        worksheet.set_column('C:D', 30)
        worksheet.set_column('D:E', 30)
        worksheet.set_column('E:F', 30)
        worksheet.set_column('F:G', 20)
        worksheet.set_column('G:H', 30)
        worksheet.set_column('H:I', 30)

        for client in clients:
            service = Service.query.filter_by(client_id=client.id).first()
            payment = Payment.query.filter_by(client_id=client.id).last()

            name = client.client_user.fullname()
            email = client.client_user.email
            contact = client.client_user.phone
            building = client.building
            house = client.house
            if service:
                package = service.service_tariff.name
            else:
                package = None

            worksheet.write(row, col, name)
            worksheet.write(row, col + 1, email)
            worksheet.write(row, col + 2, contact)
            worksheet.write(row, col + 3, building)
            worksheet.write(row, col + 4, house)
            worksheet.write(row, col + 5, package)
            if payment:
                last_payment = payment.date
                due_date = last_payment + relativedelta(months=+1, days=-1)
                worksheet.write_datetime(row, col + 6, last_payment, date_format)
                worksheet.write_datetime(row, col + 7, due_date, date_format)
            else:
                last_payment = None
                due_date = None
                worksheet.write(row, col + 6, last_payment)
                worksheet.write(row, col + 7, due_date)

            row += 1

        workbook.close()

        time.sleep(5)
        # i += 1
        task = Task.query.get(job.get_id())
        task.complete = True
        db.session.commit()

        download = Download.query.filter_by(task_id=job.get_id()).first()
        if download:
            d = datetime.now
            name = 'Data of ' + str(total_clients) + ' clients in XLS'
            download.name = name
            download.path = file_name
            download.generated = datetime.now()
            download.status = 1
            db.session.commit()

    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    # finally:
    #     _set_task_progress(100)
