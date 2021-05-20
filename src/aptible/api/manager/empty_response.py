from typing import Dict


class EmptyResponse:
    # pylint: disable=no-self-use

    def __init__(self, status_code: int = 0):
        self.status_code = status_code

    def json(self) -> Dict:
        return {}

    @property
    def ok(self) -> bool:
        return self.status_code < 400
