from .base import primary_key, Column, key_type
from .mixins import PaginatedAPIMixin

from app import db
import redis
import rq
from flask import current_app


from app.utils.data import getdate


# services = db.Table('services',
#                     Column('client_id', db.Integer, db.ForeignKey('client.id'))
#                     )


class Client(PaginatedAPIMixin, db.Model):
    __tablename__ = 'client'

    id = primary_key('client')
    building = Column(db.String(255), nullable=True)
    user_id = Column(key_type('User'), db.ForeignKey('user.id'))
    house = Column(db.String(255), nullable=True)
    location = Column(db.String(255), nullable=True)
    balance = Column(db.Integer, default=0.00)
    refundable_credit = Column(db.Integer, default=0.00)
    has_overdue_invoice = Column(db.Boolean, default=False)
    address_gps_lat = Column(db.String(128), nullable=True)
    address_gps_lon = Column(db.String(128), nullable=True)
    service = db.relationship('Service', backref='service_client', lazy='dynamic')
    package_price = Column(db.Integer, default=0.00)

    payment = db.relationship('Payment', backref='payment_client', lazy='dynamic')
    invoice = db.relationship('Invoice', backref='invoice_client', lazy='dynamic')
    email_log = db.relationship('EmailLog', backref='email_client', lazy='dynamic')

    tickets = db.relationship('Ticket', backref='ticket_client', lazy='dynamic')
    status = Column(db.String(64), server_default='active')

    def tariff(self):
        service = Service.query.filter_by(client_id=self.id).first()
        tariff = Tariff.query.filter_by(id=service.tariff_id).first()
        if tariff:
            return tariff.name
        else:
            return 'No service'

    def last_payment_date(self):
        payment = Payment.query.filter_by(client_id=self.id).order_by(Payment.id.desc()).first()
        if payment:
            return payment.date.strftime('%d %b %Y')
        else:
            return 'No payment yet'

    def invoice(self):
        invoice = Invoice.query.filter_by(client_id=self.id).filter_by(invoice_status=1).first()
        if invoice:
            return invoice.due_date.strftime('%d %b %Y')
        else:
            return 'No Invoice'


class Tariff(PaginatedAPIMixin, db.Model):
    __tablename__ = 'tariff'

    id = primary_key('Tariff')
    name = Column(db.String(255), nullable=True)
    price = Column(db.Integer, nullable=True)
    service = db.relationship('Service', backref='service_tariff', lazy='dynamic')


class Service(PaginatedAPIMixin, db.Model):
    __tablename__ = 'service'

    id = primary_key('Service')
    client_id = Column(key_type('Client'), db.ForeignKey('client.id'))
    tariff_id = Column(key_type('Tariff'), db.ForeignKey('tariff.id'))
    active_from = Column(db.DateTime)
    invoicing_start = Column(db.DateTime)
    next_invoicing_date = Column(db.DateTime)
    status = Column(db.String(64), server_default='active')
    ip = Column(db.String(64), nullable=True)
    # client = db.relationship(client, backref=db.backref("service", cascade="all, delete-orphan"))
    # tariff = db.relationship('Tariff', backref='tariff_service', lazy='dynamic')


class Payment(db.Model):
    __tablename = 'payment'

    id = primary_key('payment')
    client_id = Column(db.Integer, db.ForeignKey('client.id'))
    amount = Column(db.Integer)
    send_receipt = Column(db.Boolean, default=False)
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    note = Column(db.Text, nullable=True)
    receipt_sent_date = Column(db.DateTime, nullable=True)
    receipt_number = Column(db.String(64), nullable=True)
    method_id = Column(db.Integer, db.ForeignKey('payment_method.id'))
    date = Column(db.DateTime)


class Invoice(db.Model):
    __tablename__ = 'invoice'

    id = primary_key('invoice')
    client_id = Column(db.Integer, db.ForeignKey('client.id'))
    total = Column(db.Integer)
    amount_paid = Column(db.Integer, default=0)
    create_date = Column(db.DateTime)
    invoice_no = Column(db.String(255))
    invoice_status = Column(db.Integer, default=1)
    pdf_path = Column(db.String(128), nullable=True)
    due_date = Column(db.DateTime)
    email_sent_date = Column(db.DateTime, nullable=True)
    notes = Column(db.String(128), nullable=True)
    overdue_notification_sent = Column(db.Integer, nullable=True)
    can_cause_suspension = Column(db.Boolean, default=False)
    balance = Column(db.Integer, default=0)
    is_overdue = Column(db.Boolean, default=False, nullable=True)

    def client(self):
        from . import User
        client = Client.query.filter_by(id=self.client_id).first()
        user = User.query.filter_by(id=client.user_id).first()
        return user.fullname()

    def date_diff(self, string_ed_date, string_st_date):
        return (getdate(string_ed_date) - getdate(string_st_date)).days


class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = primary_key('ticket')
    client_id = Column(db.Integer, db.ForeignKey('client.id'))
    assigned_user = Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = Column(db.Integer, default=1)
    subject = Column(db.String(128))
    message = Column(db.Text, nullable=True)

    created_at = Column(db.DateTime, default=db.func.now())


class Department(db.Model):
    __tablename__ = 'department'

    id = primary_key('department')
    name = Column(db.String(64))


class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'

    id = primary_key('method')
    name = Column(db.String(64))
    payment = db.relationship('Payment', backref='payment_method', lazy='dynamic')


class EmailLog(db.Model):
    __tablename__ = 'email_log'

    id = primary_key('email_log')
    user_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    client_id = Column(db.Integer, db.ForeignKey('client.id'))
    invoice_id = Column(db.Integer, db.ForeignKey('invoice.id'))
    created_date = Column(db.DateTime, default=db.func.now())
    message = Column(db.Text)
    status = Column(db.Integer, default=1)
    subject = Column(db.Text, nullable=True)
    attachment = Column(db.String(128), nullable=True)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)
    file_name = db.Column(db.String(128), index=True)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class Download(db.Model):
    __tablename__ = 'download'

    id = primary_key('download')
    task_id = Column(db.String(36), db.ForeignKey('task.id'))
    name = Column(db.String(128), index=True, nullable=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    path = Column(db.String(128), index=True, nullable=True)
    created = Column(db.DateTime, index=True, default=db.func.now())
    generated = Column(db.DateTime, index=True, nullable=True)
    status = Column(db.Integer, index=True, default=2)
