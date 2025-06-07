from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='in_list')
def in_list(value, the_list):
    if isinstance(the_list, str):
        the_list = the_list.split(',')
    return str(value) in the_list

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def attr(field, attributes):
    attrs = {}
    for pair in attributes.split(','):
        name, value = pair.split(':')
        attrs[name.strip()] = value.strip()
    return field.as_widget(attrs=attrs)

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

