from django import template
from member.models import Invoice

register = template.Library()

@register.filter
def return_invoice_status(invoice):
    return Invoice.Status.labels[invoice.status].lower()
