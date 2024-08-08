import re
from django import template

register = template.Library()


@register.filter
def length_is(value, length):
    return len(value) == length


@register.filter
def clean_text(value):
    res = value.replace('\n', ' ')
    return res


@register.filter
def checkbox(value):
    res = re.sub(r"</?(?i:td)(.|\n)*?>", "", value)
    return res

@register.filter
def sum_number(value, number):
    return value + number


@register.filter
def neg_num(value, number):
    return value - number
