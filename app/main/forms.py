from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateTimeField, SelectField, TextAreaField, BooleanField, \
    PasswordField
from wtforms.validators import DataRequired, Email, Length, IPAddress
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Tariff, Client, PaymentMethod, User, Department, UserGroup
from .helpers import increment_invoice_number
from app import db


class UserForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone number', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    group = QuerySelectField('Permission group', validators=[DataRequired()],
                             blank_text="Choose a permission group",
                             get_label='name', query_factory=lambda: db.session.query(UserGroup).all())

    submit = SubmitField('Save')


class ClientForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    id_pass = StringField('I.D or Passport number', validators=[DataRequired()])
    phone = IntegerField('Phone number', validators=[DataRequired(message='Invalid phone number.')])
    email = StringField('Email address', validators=[Email()])
    house = StringField('House number')
    building = StringField('Building')
    location = StringField('Location')
    latitude = StringField('Latitude')
    longitude = StringField('Longitude')

    submit = SubmitField('Submit')


class TariffForm(FlaskForm):
    name = StringField('E.g. Internet', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired(message='Enter a valid amount')])

    submit = SubmitField('Submit')


class DepartmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Submit')


class MethodForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Submit')


class ServiceForm(FlaskForm):
    tariff = QuerySelectField('Service plan', validators=[DataRequired()],
                              blank_text="Choose a service plan",
                              get_label='name', query_factory=lambda: db.session.query(Tariff).all())
    activation = SelectField('Activation', validators=[DataRequired()],
                             choices=[('1', 'Active now'), ('2', 'Activate on date...'),
                                      ('3', 'Keep inactive (quoted) for now')])
    ip = StringField('IP address', validators= [IPAddress(message='Enter a valid IP')])

    invoicing_start = DateTimeField('Invoicing starts', default=datetime.today, format='%Y-%m-%d')
    active_from = DateTimeField('Active from')
    active_to = DateTimeField('Active to')

    submit = SubmitField('Submit')


class PaymentForm(FlaskForm):
    client = QuerySelectField('Client', validators=[DataRequired()], allow_blank=True, blank_text="Choose a client",
                              get_label='full_name', query_factory=lambda: db.session.query(User)
                              .join(Client, Client.user_id == User.id).all())
    amount = IntegerField('Amount', validators=[DataRequired(message='Invalid amount')])
    method = QuerySelectField('Paymet method', validators=[DataRequired()],
                              get_label='name', query_factory=lambda: db.session.query(PaymentMethod).all())
    created_date = DateTimeField("Created date", default=datetime.today, format='%Y-%m-%d',
                             validators=[DataRequired(message='Invalid date')])
    note = TextAreaField('Note')
    send_receipt = BooleanField('Send receipt')

    submit = SubmitField('Save')


class NewInvoiceForm(FlaskForm):
    client = QuerySelectField('Client', validators=[DataRequired()], allow_blank=True, blank_text="Choose a client",
                              get_label='full_name', query_factory=lambda: db.session.query(User)
                              .join(Client, Client.user_id == User.id).all())

    submit = SubmitField('Save')


class InvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice number', default=increment_invoice_number, validators=[DataRequired()])
    created_date = DateTimeField("Created date", default=datetime.today, format='%Y-%m-%d', validators=[DataRequired()])
    notes = TextAreaField('Invoice notes')

    submit = SubmitField('Save')
    submit_and_send = SubmitField('Save and send')


class TicketingForm(FlaskForm):
    client = QuerySelectField('Client', validators=[DataRequired()], allow_blank=True, blank_text="Choose a client",
                              get_label='full_name', query_factory=lambda: db.session.query(User)
                              .join(Client, Client.user_id == User.id).all())

    department = QuerySelectField('Department', validators=[DataRequired()], allow_blank=True,
                                  blank_text="Choose a department",
                                  get_label='name', query_factory=lambda: db.session.query(Department).all())

    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Messsage', validators=[Length(max=250)])
    submit = SubmitField('Save')


class PermissionGroup(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Save')
