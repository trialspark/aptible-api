from .resource import Resource, ResourceClassFactory


from inflection import singularize, camelize


def lookup_resource_class_by_name(name: str) -> type:
    class_name = singularize(camelize(name))

    klass = None
    try:
        klass = globals()[class_name]
    except KeyError:
        klass = ResourceClassFactory(class_name)
        globals()[class_name] = klass

    return klass
