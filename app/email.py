from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail, Config
# from optifast import app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()


# def send_invoice_email(sender, recipients, html_body, sync=False):
#     app = current_app._get_current_object()
#     msg = Message(subject='New invoice',
#                   sender=sender, recipients=recipients)
#     # with app.open_resource(Config.INVOICE_FOLDER + pdf) as pd:
#     #     msg.attach(pdf, 'application/pdf', pd.read())
#
#     msg.html = html_body
#
#     if sync:
#         mail.send(msg)
#     else:
#         Thread(target=send_async_email, args=[app, msg]).start()


def send_email(to, subject, template, pdf, sync=False, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, sender=Config.ADMINS[0], recipients=to)
    with app.open_resource(Config.INVOICE_FOLDER + pdf) as pd:
        msg.attach(pdf, 'application/pdf', pd.read())

    msg.html = render_template(template + '.html', **kwargs)
    # msg.body = render_template(template + '.txt', **kwargs)

    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=[app, msg]).start()
