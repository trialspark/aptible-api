from inflection import singularize, camelize

from .resource import Resource


def ResourceClassFactory(name):
    def __init__(self, **kwargs):
        Resource.__init__(self, **kwargs)
    return type(name, (Resource, ), {"__init__": __init__})


def lookup_resource_class_by_name(name: str) -> type:
    class_name = singularize(camelize(name))

    klass = None
    try:
        klass = globals()[class_name]
    except KeyError:
        klass = ResourceClassFactory(class_name)
        globals()[class_name] = klass

    return klass
