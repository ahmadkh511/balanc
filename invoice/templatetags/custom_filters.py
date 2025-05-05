from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """إرجاع قيمة من القاموس حسب المفتاح"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
