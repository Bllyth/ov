import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'secret-key'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/optifast'
    SQLALCHEMY_DATABASE_URI = 'postgresql://root:root@localhost:5432/ov'
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    REDIS_URL = 'redis://'

    ADMINS = ['admin@admin.com']
    MAIL_SERVER = ''
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_SUBJECT_PREFIX = '[New invoice]'
    MAIL_DEBUG = True

    INVOICE_FOLDER = os.path.join(basedir, 'invoices/')
    EXCEL_FOLDER = os.path.join(basedir, 'excel/')
    RECEIPT_FOLDER = os.path.join(basedir, 'receipts')
