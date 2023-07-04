from django import template

register = template.Library()


@register.filter
def get(row, attr):
    if isinstance(row, dict):
        value = row.get(attr)
    else:
        try:
            value = getattr(row, attr, None)
        except TypeError:
            value = row[attr]
    if value is None:
        value = ""
    return value
