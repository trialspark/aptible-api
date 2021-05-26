from .resource import Resource


class EmptyResource(Resource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, name: str) -> None:
        return None

    @property
    def empty(self) -> bool:
        return True
