from .api_manager import ApiManager


class AptibleAuthApi(ApiManager):
    # pylint: disable=inconsistent-return-statements

    def __init__(self, api_url_base: str = "https://auth.aptible.com"):
        super().__init__(api_url_base=api_url_base)
