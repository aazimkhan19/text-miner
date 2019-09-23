from django import template

register = template.Library()

@register.filter(name="group_name")
def group_name(user, group):
    print("groups", user, group, user.groups.all())
    return user.groups.filter(name=group).exists()