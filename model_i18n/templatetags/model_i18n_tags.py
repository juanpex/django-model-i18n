# -*- coding: utf-8 -*-
from django import template


class GetAttrFromInstanceNode(template.Node):
    def __init__(self, obj, attrname, var=None):
        self.obj = template.Variable(obj)
        self.attrname = template.Variable(attrname)
        self.var = var

    def __repr__(self):
        return "<GetAttrFromInstanceNode>"

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            obj = None
        if not obj.pk:
            return ''
        try:
            attrname = self.attrname.resolve(context)
        except template.VariableDoesNotExist:
            attrname = None
        try:
            data = getattr(obj, '_'.join((attrname, 'master')))
        except:
            data = getattr(obj, attrname,)
        if callable(data):
            data = data()
        data = data or ''
        if isinstance(data, (unicode, str)):
            data = data.replace("'", "&#39;").replace('"', "&quot;")
        if self.var:
            context.update({self.var: data})
            return ''
        return data


def get_attr(parser, token):
    args = token.contents.split()
    if len(args) < 3:
        raise template.TemplateSyntaxError, ('"%s" requires two variables (got %r)' % (args[0], args))
    obj = args[1]
    attrname = args[2]
    var = None
    if len(args) > 4:
        if args[-2] != 'as':
            raise template.TemplateSyntaxError, ('"%s" requires "as variable" '
                                    'as last arguments (got %r)' % (args[0], args))
        var = args[-1]
    return GetAttrFromInstanceNode(obj, attrname, var)

register = template.Library()
register.tag(get_attr)
