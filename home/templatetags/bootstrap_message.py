from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def bootstrap_message(message):
    tag = 'danger' if  message.tags == 'error' else message.tags
    return mark_safe(f"<div class='alert alert-{tag}' role='alert'>{message}</div>")