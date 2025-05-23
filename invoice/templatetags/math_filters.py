from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    """طرح arg من value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0