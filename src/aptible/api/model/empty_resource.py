from .resource import Resource


class EmptyResource(Resource):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def empty(self) -> bool:
        return True
