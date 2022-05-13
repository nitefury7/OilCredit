from django import template
from member.models import Invoice

register = template.Library()


@register.filter
def invoice_color_bootstrap(invoice):
    return {
        Invoice.Status.APPROVED: 'success',
        Invoice.Status.PENDING: 'light',
        Invoice.Status.REJECTED: 'danger',
    }[invoice.status]
