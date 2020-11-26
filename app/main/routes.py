import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_login import login_required, current_user
from flask import request, render_template, url_for, flash, redirect, session, send_from_directory, Markup

from . import main
from ..models import User, Client, Tariff, Service, Payment, Invoice, Ticket, UserGroup, Department, PaymentMethod, \
    EmailLog, Download
from .forms import ClientForm, TariffForm, ServiceForm, PaymentForm, InvoiceForm, NewInvoiceForm, TicketingForm, \
    UserForm, PermissionGroup, DepartmentForm, MethodForm
from app import db, settings, Config
from app.email import send_email

from flask_weasyprint import HTML, render_pdf
from xhtml2pdf import pisa
import xlsxwriter

from rq import get_current_job

from app.permissions import require_permission, require_admin


# Utility function
@login_required
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        source_html,  # the HTML to convert
        dest=result_file)  # file handle to recieve result

    # close output file
    result_file.close()  # close output file

    # return False on success and True on errors
    return pisa_status.err


@main.route('/client/export')
@login_required
def client_export():
    if current_user.get_task_in_progress('export_clients'):
        job = get_current_job()
        flash('An export task is in progress', 'warning')
        # print(job.get_id())
    else:
        current_user.launch_task('export_clients', 'Exporting clients...')
        db.session.commit()

        # job = get_current_job()
        #
        # clients = Client.query.all()
        # total_clients = Client.query.count()
        #
        # file_name = 'clients' + "-" + str(time.time()) + '.xlsx'
        # workbook = xlsxwriter.Workbook(Config.EXCEL_FOLDER + file_name)
        # # Add a bold format to use to highlight cells.
        # bold = workbook.add_format({'bold': True})
        #
        # worksheet = workbook.add_worksheet()
        #
        # date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
        #
        # # Start from the first cell. Rows and columns are zero indexed.
        # row = 1
        # col = 0
        #
        # worksheet.write('A1', 'Name', bold)
        # worksheet.write('B1', 'Email', bold)
        # worksheet.write('C1', 'Contact', bold)
        # worksheet.write('D1', 'Building', bold)
        # worksheet.write('E1', 'House number', bold)
        # worksheet.write('F1', 'Package', bold)
        # worksheet.write('G1', 'Last payment date', bold)
        # worksheet.write('H1', 'Due date', bold)
        #
        # worksheet.set_column('A:B', 30)
        # worksheet.set_column('B:C', 30)
        # worksheet.set_column('C:D', 30)
        # worksheet.set_column('D:E', 30)
        # worksheet.set_column('E:F', 30)
        # worksheet.set_column('F:G', 20)
        # worksheet.set_column('G:H', 30)
        # worksheet.set_column('H:I', 30)
        #
        # for client in clients:
        #     service = Service.query.filter_by(client_id=client.id).first()
        #     payment = Payment.query.filter_by(client_id=client.id).first()
        #
        #     name = client.client_user.fullname()
        #     email = client.client_user.email
        #     contact = client.client_user.phone
        #     building = client.building
        #     house = client.house
        #     if service:
        #         package = service.service_tariff.name
        #     else:
        #         package = None
        #
        #     worksheet.write(row, col, name)
        #     worksheet.write(row, col + 1, email)
        #     worksheet.write(row, col + 2, contact)
        #     worksheet.write(row, col + 3, building)
        #     worksheet.write(row, col + 4, house)
        #     worksheet.write(row, col + 5, package)
        #     if payment:
        #         last_payment = payment.date
        #         due_date = last_payment + relativedelta(months=+1, days=-1)
        #         worksheet.write_datetime(row, col + 6, last_payment, date_format)
        #         worksheet.write_datetime(row, col + 7, due_date, date_format)
        #     else:
        #         last_payment = None
        #         due_date = None
        #         worksheet.write(row, col + 6, last_payment)
        #         worksheet.write(row, col + 7, due_date)
        #
        #     row += 1
        #
        # workbook.close()
        #
        # print(job.getid())
        #
        # time.sleep(15)
        #
        #
        # download = Download.query.filter_by(task_id=job.get_id()).first()
        # if download:
        #     d = datetime.no
        #     name = 'Data of ' + str(total_clients) + ' clients in XLS'
        #     download.name = name
        #     download.path = file_name
        #     download.generated = datetime.now()
        #     download.status = 1
        #     db.session.commit()
        #
        # # if current_user.get_task_in_progress('export_clients'):
        # #     flash('An export task is in progress', 'warning')
        # # else:
        # #     current_user.launch_task('export_clients', 'Exporting clients...')
        # #     db.session.commit()
        flash('Export was added to queue. You can download it in Settings -> Downloads', 'success')

    return redirect(url_for('main.clients'))


@main.route('/system/downloads')
@login_required
def downloads():
    downloads = Download.query.all()
    return render_template('download/downloads.html', downloads=downloads)


@main.route('/system/downloads/<filename>')
@login_required
def clients_report_download(filename):
    return send_from_directory(Config.EXCEL_FOLDER, filename, as_attachment=True)


@main.route('/invoice-pdf')
@login_required
def invoice_pdf():
    invoice = Invoice.query.filter_by(id=4).first()
    client = Client.query.filter_by(id=2).first()
    service = Service.query.filter_by(client_id=client.id).first()

    return render_template('invoice-templates/template.html', invoice=invoice, client=client, service=service)


@login_required
def generate_pdf():
    invoice = Invoice.query.filter_by(id=4).first()
    client = Client.query.filter_by(id=2).first()
    service = Service.query.filter_by(client_id=client.id).first()
    html = render_template('invoice-templates/template.html', invoice=invoice, client=client, service=service,
                           name=invoice.invoice_no)
    pdf = HTML(string=html).write_pdf()
    if Config.INVOICE_FOLDER:
        f = open(Config.INVOICE_FOLDER + invoice.invoice_no + '.pdf', 'wb')
        f.write(pdf)

        return url_for('main.invoices')


@main.route('/')
@login_required
def index():
    name = 1
    clients_count = db.session.query(func.count(Client.id)).scalar()
    overdue_invoices_count = db.session.query(func.count(Invoice.id)).filter(Invoice.is_overdue == True).scalar()

    overdue_invoices = Invoice.query.filter_by(is_overdue=True).limit(3).all()

    today = datetime.today()

    return render_template('dashboard.html', clients_count=clients_count, name=name,
                           overdue_invoices_count=overdue_invoices_count, overdue_invoices=overdue_invoices,
                           today=today)


@main.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = db.session.query(User).outerjoin(Client, Client.user_id == User.id).filter(Client.user_id == None).all()

    # users = User.query.all()
    form = UserForm()

    # user = User.query.filter_by(user=form.user_id.data).first()

    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            group=request.form['group']
        )
        user.full_name = user.first_name + ' ' + user.last_name
        user.username = user.email
        user.hash_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('User has been created', 'success')
        return redirect(url_for('main.users'))

    # if user:
    #     if form.validate_on_submit():
    #         user.first_name = form.first_name.data
    #         user.last_name = form.last_name.data
    #         user.email = form.email.data
    #         user.phone = form.phone.data
    #         user.group = request.form['group']
    #
    #         flash('User has been edited', 'success')
    #         return redirect(url_for('main.users'))
    #
    #     elif request.method == 'GET':
    #         form.first_name.data = user.first_name
    #         form.last_name.data = user.last_name
    #         form.email.data = user.email
    #         form.phone.data = user.phone
    #         request.form['group'] = user.group

    return render_template('user/users.html', users=users, form=form)


@main.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = UserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.group = request.form['group']
        user.password_hash = user.hash_password(form.password.data)

        db.session.commit()

        flash('User edited sucessfully', 'success')
        return redirect(url_for('main.users'))

    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.phone.data = user.phone
        # request.form['group'] = user.group
    return render_template('user/edit-user.html', form=form)


@main.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully', 'success')

    return redirect(url_for('main.users'))


@main.route('/system/security/permission-groups/new', methods=['GET', 'POST'])
@login_required
def new_user_group():
    form = PermissionGroup()

    if form.validate_on_submit():
        group = UserGroup(
            name=form.name.data
        )

        db.session.add(group)
        db.session.commit()

        flash('User group has been created', 'success')
        return redirect(url_for('main.user_groups'))

    return render_template('user/new-group.html', form=form)


@main.route('/system/security/permission-groups')
@login_required
def user_groups():
    groups = UserGroup.query.all()

    return render_template('user/groups.html', groups=groups)


@main.route('/system/security/permission-groups/<int:group_id>')
@login_required
def user_group(group_id):
    group = UserGroup.query.get_or_404(group_id)

    return render_template('user/group.html', group=group)


@main.route('/client/new', methods=['GET', 'POST'])
@login_required
def new_client():
    form = ClientForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            id_passport=form.id_pass.data
        )
        user.full_name = user.first_name + ' ' + user.last_name
        user.username = user.email
        db.session.add(user)
        db.session.flush()

        client = Client(
            user_id=user.id,
            house=form.house.data,
            building=form.building.data,
            location=form.location.data

        )
        db.session.add(client)
        db.session.commit()
        flash('Client has been created', 'success')
        return redirect(url_for('main.client', client_id=client.id))

    return render_template('client/new-client.html', form=form)


@main.route('/client/all')
@login_required
def clients():
    form = ClientForm()
    clients = Client.query.filter_by(status='active').order_by(Client.id.asc()).all()


    # clients = Client.query.outerjoin()
    # service = Service.query.filter_by().all()
    # clients = Client.query.outerjoin(Service, Client.id == Service.client_id).all()
    # clients = db.session.query(Client, Service, Payment, Invoice).leftjoin(Service, Client.id == Service.client_id) \
    #     .leftjoin(Payment, Client.id == Payment.client_id).leftjoin(Invoice, Client.id == Invoice.client_id)\
    #     .filter(Client.status == 'active').all()
    delta = relativedelta(months=+1, days=-1)

    print(clients, delta)

    return render_template('client/clients.html', clients=clients, delta=delta, form=form)


@main.route('/client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def client(client_id):
    form = ClientForm()
    client = Client.query.get_or_404(client_id)
    service = Service.query.filter_by(client_id=client_id).first()

    # client = db.session.query(Service, Client).filter(Service.client_id == Client.id).first()
    # service = Service.query.filter_by(client_id=client_id).first()
    # initials = ''.join([x[0].upper() for x in client.client_user.full_name.split(' ')])
    return render_template('client/client.html', client=client, service=service, form=form)


@main.route('/client/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    form = ClientForm()
    client = Client.query.get_or_404(client_id)
    user = User.query.filter_by(id=client.user_id).first()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.id_passport = form.id_pass.data

        user.full_name = user.first_name + ' ' + user.last_name
        user.username = user.email
        db.session.add(user)

        client.house = form.house.data
        client.building = form.building.data
        client.location = form.location.data

        db.session.add(client)
        db.session.commit()

        flash('Client edited sucessfully', 'success')
        return redirect(url_for('main.clients'))

    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.phone.data = user.phone
        form.id_pass.data = user.id_passport

        form.house.data = client.house
        form.building.data = client.building
        form.location.data = client.location
        form.latitude.data = client.address_gps_lat
        form.longitude.data = client.address_gps_lon

    return render_template('client/new-client.html', form=form)


@main.route('/client/delete/<int:client_id>', methods=['GET', 'POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    service = Service.query.filter_by(client_id=client_id).first()
    # ticket = Ticket.query.filter_by(client_id=client_id).first()

    if service:
        flash('You can not delete a client with an active service', 'warning')
        return redirect(url_for('main.client', client_id=client_id))
    else:
        client.status = 'inactive'
        db.session.commit()
        flash('Client deleted successfully', 'success')
        return redirect(url_for('main.clients'))


@main.route('/client/<int:client_id>/invoice')
@login_required
def client_invoice(client_id):
    form = ClientForm()
    client = Client.query.filter_by(id=client_id).first()
    invoices = Invoice.query.filter_by(client_id=client_id).all()
    return render_template('client/client.html', client=client, invoices=invoices, form=form)


@main.route('/client/<int:client_id>/ticket')
@login_required
def client_ticket(client_id):
    form = ClientForm()
    client = Client.query.get_or_404(client_id)
    tickets = Ticket.query.filter_by(client_id=client_id).all()
    return render_template('client/client.html', client=client, tickets=tickets, form=form)


@main.route('/service/new/<int:client_id>', methods=['GET', 'POST'])
@login_required
def new_service(client_id):
    form = ServiceForm()

    if form.validate_on_submit():
        service = Service(
            client_id=client_id,
            tariff_id=request.form['tariff'],
            invoicing_start=form.invoicing_start.data,
            # active_from=date.today(),
            next_invoicing_date=form.invoicing_start.data + relativedelta(months=+1, days=-3),
            ip=form.ip.data

        )

        if form.activation.data == '1':
            service.active_from = date.today()
        elif form.activation.data == '2':
            service.active_from = form.activation.data

        db.session.add(service)
        db.session.commit()

        flash('Service plan has been added', 'success')
        return redirect(url_for('main.client', client_id=client_id))

    return render_template('service/new-service.html', form=form)


@main.route('/client/service/<int:client_id>', methods=['GET', 'POST'])
@login_required
def activate_service(client_id):
    # form = ServiceForm()
    # service = Service.query.filter_by(client_id=client_id).first()
    # client = Client.query.get_or_404(client_id)

    service = Service.query.filter_by(client_id=client_id).first()
    service.status = 'active'
    db.session.commit()

    return redirect(url_for('main.client', client_id=client_id))
    #
    # return render_template('service/new-service.html', service=service, client=client, form=form)


@main.route('/client/end-service/<int:service_id>')
@login_required
def end_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    service.status = 'ended'
    db.session.commit()

    flash('Service plan ended', 'success')

    return redirect(url_for('main.client', client_id=service.client_id))


@main.route('/client/service/delete/<int:client_id>')
@login_required
def delete_service(client_id):
    service = Service.query.filter_by(client_id=client_id).first()
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully', 'success')

    return redirect(url_for('main.client', client_id=client_id))


@main.route('/system/service-plans')
@login_required
def tariffs():
    form = TariffForm()
    tariffs = Tariff.query.all()
    services = db.session.query(func.count(Service.id)) \
        .join(Tariff, Tariff.id == Service.tariff_id).scalar()
    return render_template('tariff/tariffs.html', tariffs=tariffs, services=services, form=form)


@main.route('/system/items/service-plans/new', methods=['GET', 'POST'])
@login_required
def new_tariff():
    form = TariffForm()
    if form.validate_on_submit():
        tariff = Tariff(
            name=form.name.data,
            price=form.price.data
        )
        db.session.add(tariff)
        db.session.commit()
        flash('Tariff added successfully', 'success')
        return redirect(url_for('main.tariffs'))
    return render_template('tariff/new_tariff.html', form=form)


@main.route('/system/items/service-plans/<int:tariff_id>', methods=['GET', 'POST'])
@login_required
def tariff(tariff_id):
    tariff = Tariff.query.get_or_404(tariff_id)
    return render_template('tariff/tariffs.html', tariff=tariff)


@main.route('/system/items/service-plans/edit/<int:tariff_id>', methods=['GET', 'POST'])
@login_required
def edit_tariff(tariff_id):
    tariff = Tariff.query.get_or_404(tariff_id)
    form = TariffForm()
    if form.validate_on_submit():
        tariff.name = form.name.data
        tariff.price = form.price.data

        db.session.add(tariff)
        db.session.commit()
        flash('Service plan edited successfully', 'success')
        return redirect(url_for('main.tariffs'))

    elif request.method == 'GET':
        form.name.data = tariff.name
        form.price.data = tariff.price

    return render_template('tariff/new_tariff.html', tariff=tariff, form=form)


@main.route('/system/items/service-plans/delete/<int:tariff_id>', methods=['GET', 'POST'])
@login_required
def delete_tariff(tariff_id):
    service = Service.query.filter_by(tariff_id=tariff_id).first()
    tariff = Tariff.query.get_or_404(tariff_id)
    if service:
        flash("You can not delete a service plan with active services", 'warning')
        return redirect(url_for('main.tariffs'))
    else:
        db.session.delete(tariff)
        db.session.commit()
        flash("Service plan deleted successfully", 'success')
        return redirect(url_for('main.tariffs'))


@main.route('/system/items/departments/new', methods=['GET', 'POST'])
@login_required
def new_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(
            name=form.name.data
        )
        db.session.add(department)
        db.session.commit()
        return redirect(url_for('main.departments'))
    return render_template('department/new_department.html', form=form)


@main.route('/system/items/departments')
@login_required
def departments():
    form = DepartmentForm()
    departments = Department.query.all()
    return render_template('department/departments.html', departments=departments, form=form)


@main.route('/system/items/departments/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    form = DepartmentForm()
    department = Department.query.get_or_404(department_id)
    if form.validate_on_submit():
        department.name = form.name.data
        db.session.add(department)
        db.session.commit()

        flash('Deparment edited successfully', 'success')
        return redirect(url_for('main.departments'))

    elif request.method == 'GET':
        form.name.data = department.name

    return render_template('department/new_department.html', form=form)


@main.route('/system/items/departments/delete/<int:department_id>', methods=['GET', 'POST'])
@login_required
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)

    db.session.delete(department)
    db.session.commit()

    flash('Department deleted successfully', 'success')

    return redirect(url_for('main.departments'))


@main.route('/system/items/billing/payment-methods/new', methods=['GET', 'POST'])
@login_required
def new_payment_method():
    form = MethodForm()
    if form.validate_on_submit():
        method = PaymentMethod(
            name=form.name.data
        )
        db.session.add(method)
        db.session.commit()
        flash('Payment method added successfully', 'success')
        return redirect(url_for('main.payment_methods'))
    return render_template('payment-methods/new-payment-method.html', form=form)


@main.route('/system/items/billing/payment-methods')
@login_required
def payment_methods():
    form = MethodForm()
    methods = PaymentMethod.query.all()
    return render_template('payment-methods/payment-methods.html', methods=methods, form=form)


@main.route('/system/items/billing/payment-methods/edit/<int:method_id>', methods=['GET', 'POST'])
@login_required
def edit_payment_method(method_id):
    form = MethodForm()
    method = Payment.query.get_or_404(method_id)
    if form.validate_on_submit():
        method.name = form.name.data
        db.session.add(method)
        db.session.commit()

        flash('Payment method edited successfully', 'success')
        return redirect(url_for('main.payment_methods'))

    elif request.method == 'GET':
        form.name.data = method.name

    return render_template('payment-methods/payment-methods.html', form=form)


@main.route('/system/items/billing/payment-methods/delete/<int:method_id>', methods=['GET', 'POST'])
@login_required
def delete_method(method_id):
    method = PaymentMethod.query.get_or_404(method_id)

    db.session.delete(method)
    db.session.commit()

    flash('method deleted successfully', 'success')

    return redirect(url_for('main.payment_methods'))


# Invoice status's
# 1 - Unpaid
# 2-Partial payment_methods
# 3 - Fully paid
# 4 - Overdue

@main.route('/client/invoice/new/<int:client_id>', methods=['GET', 'POST'])
@login_required
def new_invoice(client_id):
    form = InvoiceForm()
    service = Service.query.filter_by(client_id=client_id).first()
    client = Client.query.get_or_404(client_id)
    if service is None:
        flash('Create a service for this user first', 'warning')
        return redirect(url_for('main.new_service', client_id=client_id))
    else:
        if form.validate_on_submit():
            invoice = Invoice(
                client_id=client_id,
                total=service.service_tariff.price,
                create_date=form.created_date.data,
                invoice_no=form.invoice_number.data,
                notes=form.notes.data,
                due_date=form.created_date.data + relativedelta(days=+3),
                balance=service.service_tariff.price
            )

            client.balance = client.balance + invoice.total
            invoice.pdf_path = invoice.invoice_no + '.pdf'

            html = render_template('invoice-templates/template.html', invoice=invoice, client=client, service=service)
            pdf = HTML(string=html).write_pdf()
            if Config.INVOICE_FOLDER:
                f = open(Config.INVOICE_FOLDER + invoice.pdf_path, 'wb')
                f.write(pdf)

            db.session.add(invoice)
            db.session.commit()
            flash('Invoice created successfully', 'success')

            if form.submit_and_send.data:
                d_email = 'sales@optifast.co.ke'
                # send_invoice_email(sender=app.config['ADMINS'][0], recipients=client.client_user.email,
                #                    html_body=render_template('mail/invoice.html', client=client, invoice=invoice),
                #                    sync=True)

                send_email(to=[client.client_user.email], subject='New invoice',
                                   template='mail/invoice', pdf=str(invoice.pdf_path), client=client, invoice=invoice)

                # send_invoice_email(sender=Config.ADMINS[0], recipients=[client.client_user.email],
                #                    html_body=render_template('mail/invoice.html', client=client, invoice=invoice),
                #                    attachments=[(invoice.pdf_path, 'application/pdf')],
                #                    sync=True)

                flash('Invoice has been queued or sending', 'success')

                log = EmailLog(user_id=current_user.id, client_id=client_id, invoice_id=invoice.id,
                               subject="New invoice", attachment=invoice.pdf_path, message='New Invoice')
                db.session.add(log)
                db.session.commit()

            return redirect(url_for('main.client', client_id=client_id))

    return render_template('invoice/new_invoice.html', form=form, service=service)


@main.route('/billing/invoices', methods=['GET', 'POST'])
@login_required
def invoices():
    form = NewInvoiceForm()
    invoices = Invoice.query.all()

    if form.validate_on_submit():
        client = Client.query.filter_by(user_id=request.form['client']).first()
        client_id = client.id
        return redirect(url_for('main.new_invoice', client_id=client_id))
    return render_template('invoice/invoices.html', invoices=invoices, form=form)


@main.route('/billing/invoices/delete/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    client = Client.query.filter_by(id=invoice.client_id).first()
    client.balance = client.balance - invoice.total
    db.session.delete(invoice)
    db.session.commit()

    flash('Invoice deleted successfully', 'success')

    return redirect(url_for('main.invoices'))


@main.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    form = PaymentForm()
    payments = Payment.query.all()

    if form.validate_on_submit():
        client = Client.query.filter_by(user_id=request.form['client']).first()
        invoice = Invoice.query.filter_by(client_id=client.id).first()
        payment = Payment(
            client_id=client.id,
            amount=form.amount.data,
            send_receipt=form.send_receipt.data,
            note=form.note.data,
            date=form.created_date.data,
            method_id=request.form['method'],
            user_id=client.client_user.id,

        )
        if invoice is None:
            client.refundable_credit = payment.amount

            db.session.add(payment)
            db.session.commit()

            flash(payment.amount, 'success')

            return redirect(url_for('main.payments'))
        else:
            if payment.amount > invoice.total:
                balance = payment.amount - client.balance
                invoice.amount_paid = invoice.total
                invoice.balance = 0
                client.balance = client.balance - invoice.total
                invoice.invoice_status = 3
                client.refundable_credit = balance
            else:
                balance = invoice.balance - payment.amount
                invoice.amount_paid = payment.amount
                invoice.balance = balance
                client.balance = client.balance - payment.amount
                invoice.invoice_status = 2

            db.session.add(payment)
            db.session.commit()

            flash('Payment added successfully', 'success')
            return redirect(url_for('main.payments'))

    return render_template('payment/payments.html', form=form, payments=payments)


# @main.route('/payment/edit/<int:payment_id>')
# @login_required
# def edit_payment(payment_id):
#     form = PaymentForm()
#     payment = Payment.query.get_or_404(payment_id)
#
#     if form.validate_on_submit():
#         payment.amount = form.amount.data
#         send_receipt = form.send_receipt.data,
#         note = form.note.data,
#         date = form.created_date.data,
#         method_id = request.form['method'],
#         user_id = 2,
#
#
#     return render_template('payment/payment.html', payment=payment)


@main.route('/payment/delete/<int:payment_id>')
@login_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()


@main.route('/schedule')
@login_required
def schedules():
    return render_template('schedule/scheduling.html')


@main.route('/ticketing', methods=['GET', 'POST'])
@login_required
def tickets():
    form = TicketingForm()
    tickets = Ticket.query.all()
    if form.validate_on_submit():
        client = Client.query.filter_by(user_id=request.form['client']).first()
        ticket = Ticket(
            client_id=client.id,
            subject=form.subject.data,
            message=form.message.data,
            # user_id=request.form['client']

        )
        db.session.add(ticket)
        db.session.commit()

        flash('Ticket created successfully', 'success')
    return render_template('ticket/tickets.html', form=form, tickets=tickets)


@main.route('/billing/invoice-revenue')
@login_required
def reports():
    invoices = Invoice.query.all()
    total = db.session.query(func.sum(Invoice.total)).scalar()
    total_unpaid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 1).scalar()
    total_overdue = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 4).scalar()
    paid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 3).scalar()
    return render_template('report/reports.html', invoices=invoices, total=total, paid=paid,
                           total_overdue=total_overdue,
                           total_unpaid=total_unpaid)


@main.route('/billing/invoiced-revenue/unpaid-invoices')
@login_required
def report_unpaid():
    invoices = Invoice.query.filter_by(invoice_status=1).all()
    total = db.session.query(func.sum(Invoice.total)).scalar()
    total_unpaid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 1).scalar()
    total_overdue = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 4).scalar()
    paid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 3).scalar()
    return render_template('report/unpaid_invoices.html', invoices=invoices, total=total, paid=paid,
                           total_overdue=total_overdue,
                           total_unpaid=total_unpaid)


@main.route('/billing/invoiced-revenue/overdue-invoices')
@login_required
def report_unpaid_overdue():
    invoices = Invoice.query.filter_by(invoice_status=4).all()
    total = db.session.query(func.sum(Invoice.total)).scalar()
    total_unpaid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 1).scalar()
    total_overdue = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 2).scalar()
    paid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 3).scalar()
    return render_template('report/unpaid_overdue_revenue.html', invoices=invoices, total=total, paid=paid,
                           total_overdue=total_overdue,
                           total_unpaid=total_unpaid)


@main.route('/billing/invoiced-revenue/paid-invoices')
@login_required
def report_paid():
    invoices = Invoice.query.filter_by(invoice_status=3).all()
    total = db.session.query(func.sum(Invoice.total)).scalar()
    total_unpaid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 1).scalar()
    total_overdue = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 4).scalar()
    paid = db.session.query(func.sum(Invoice.total)).filter(Invoice.invoice_status == 3).scalar()
    return render_template('report/paid_invoices.html', invoices=invoices, total=total, paid=paid,
                           total_overdue=total_overdue,
                           total_unpaid=total_unpaid)


@main.route('/system/logs/email')
@login_required
def logs():
    emails = EmailLog.query.all()
    return render_template('log/logs.html', emails=emails)
