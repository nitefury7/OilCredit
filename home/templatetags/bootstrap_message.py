from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def bootstrap_message(message):
    tag = 'danger' if message.tags == 'error' else message.tags
    icons = {
        'success': 'check',
        'danger': 'xmark',
        'warning': 'exclamation',
        'info': 'info',
    }
    icon = icons.get(tag, icons['info'])
    return mark_safe(
        f"<div class='fw-bold alert alert-{tag} d-flex align-items-center' role='alert'>"
        f"<i class='fs-3 me-2 fa-solid fa-circle-{icon}'></i>"
        f"{message}"
        '<button type="button" class="ms-auto btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
        f"</div>"
    )
