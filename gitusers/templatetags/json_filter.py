import bleach
import json as jsonlib
from django.utils.safestring import mark_safe


from django import template

register = template.Library()


@register.filter
def json(value):
    """safe jsonify filter, bleaches the json string using the bleach html tag remover"""
    uncleaned = jsonlib.dumps(value)
    clean = bleach.clean(uncleaned)
    return mark_safe(clean)
