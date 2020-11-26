# import time
# import sys
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from app import create_app
# from rq import get_current_job
# from app import db
# from app.models import Task, Client
# import xlsxwriter
# from app import Config
#
# app = create_app()
# app.app_context().push()
#
#
# def _set_task_progress(progress):
#     job = get_current_job()
#     if job:
#         job.meta['progress'] = progress
#         job.save_meta()
#         task = Task.query.get(job.get_id())
#         task.user.add_notification('task_progress', {'task_id': job.get_id(),
#                                                      'progress': progress})
#         if progress >= 100:
#             task.complete = True
#         db.session.commit()
#
#
# def export_clients():
#     try:
#         clients = Client.query.all()
#         total_clients = clients.count()
#         _set_task_progress(0)
#         i =0
#         file_name = 'clients' + "-" + str(time.time())
#         workbook = xlsxwriter.Workbook(Config.EXCEL_FOLDER + file_name + '.xlsx')
#         # Add a bold format to use to highlight cells.
#         bold = workbook.add_format({'bold': True})
#
#         worksheet = workbook.add_worksheet()
#
#         date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
#
#         # Start from the first cell. Rows and columns are zero indexed.
#         row = 1
#         col = 0
#
#         worksheet.write('A1', 'Name', bold)
#         worksheet.write('B1', 'Email', bold)
#         worksheet.write('C1', 'Contact', bold)
#         worksheet.write('D1', 'Building', bold)
#         worksheet.write('E1', 'House number', bold)
#         worksheet.write('F1', 'Package', bold)
#         worksheet.write('G1', 'Last payment date', bold)
#         worksheet.write('H1', 'Due date', bold)
#
#         worksheet.set_column('A:B', 30)
#         worksheet.set_column('B:C', 30)
#         worksheet.set_column('C:D', 30)
#         worksheet.set_column('D:E', 30)
#         worksheet.set_column('E:F', 30)
#         worksheet.set_column('F:G', 20)
#         worksheet.set_column('G:H', 30)
#         worksheet.set_column('H:I', 30)
#
#
#
#         for client in clients:
#             name = client.client_user.fullname()
#             email = client.client_user.email
#             contact = client.client_user.phone
#             building = client.building
#             house = client.house
#             package = '5 MBPS'
#             last_payment = datetime.today()
#             due_date = last_payment + relativedelta(months=+1, days=-1)
#
#             # # Convert the date string into a datetime object.
#             # date = datetime.strptime(date_str, "%Y-%m-%d")
#             # ...
#             # worksheet.write_datetime(row, col + 1, date, date_format)
#
#             worksheet.write(row, col, name)
#             worksheet.write(row, col + 1, email)
#             worksheet.write(row, col + 2, contact)
#             worksheet.write(row, col + 3, building)
#             worksheet.write(row, col + 4, house)
#             worksheet.write(row, col + 5, package)
#             worksheet.write_datetime(row, col + 6, last_payment, date_format)
#             worksheet.write_datetime(row, col + 7, due_date, date_format)
#
#             row += 1
#
#             # f_name = name.replace(" ", "_").lower()
#             # file_name = f_name + "-" + str(time.time())
#             #
#             # generateExcel(name, email, contact, building, house, package, last_payment, due_date, file_name)
#         workbook.close()
#
#         time.sleep(5)
#         i += 1
#         _set_task_progress(100 * i // total_clients)
#
#         download = Download
#
#     except:
#         app.logger.error('Unhandled exception', exc_info=sys.exc_info())
#     finally:
#         _set_task_progress(100)