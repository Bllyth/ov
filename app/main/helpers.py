
from app.models import Invoice


def increment_invoice_number():
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if not last_invoice:
        return 'OV0001'
    invoice_no = last_invoice.invoice_no
    invoice_int = int(invoice_no.split('OV')[-1])
    width = 4
    new_invoice_int = invoice_int + 1
    formatted = (width - len(str(new_invoice_int))) * "0" + str(new_invoice_int)
    new_invoice_no = 'OV' + str(formatted)
    return new_invoice_no
