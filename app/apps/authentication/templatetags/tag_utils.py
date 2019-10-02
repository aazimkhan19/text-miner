from django import template

register = template.Library()

@register.filter(name="group_name")
def group_name(user, group):
    return user.groups.filter(name=group).exists()