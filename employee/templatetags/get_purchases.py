from django import template
from customer.models import Purchase

register = template.Library()


@register.filter
def get_purchases(invoice):
    return Purchase.objects.filter(invoice=invoice.pk)
