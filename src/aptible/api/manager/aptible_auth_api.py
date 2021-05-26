from .api_manager import ApiManager


class AptibleAuthApi(ApiManager):
    # pylint: disable=inconsistent-return-statements

    def __init__(self, api_base: str = "https://auth.aptible.com"):
        super().__init__(api_base=api_base)
