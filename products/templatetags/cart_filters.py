from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def sum_price(items):
    total = sum(item.product.price * item.quantity for item in items)
    return total
