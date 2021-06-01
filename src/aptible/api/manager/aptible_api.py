from typing import Dict

from .api_manager import ApiManager
from .aptible_auth_api import AptibleAuthApi


class AptibleApi(ApiManager):
    # pylint: disable=inconsistent-return-statements, too-many-arguments

    def __init__(self, api_url_base: str = "https://api.aptible.com"):
        self._token = None
        self.bearer_token = None
        super().__init__(api_url_base=api_url_base)

    def authorize(
        self,
        token: str = None,
        email: str = None,
        password: str = None,
        scope: str = "manage",
        expires_in: int = 86400,
        otp_token: str = None
    ) -> bool:
        if token:
            self.bearer_token = token

        else:
            auth_api = AptibleAuthApi()
            self._token = auth_api.create_token(
                grant_type="password",
                username=email,
                password=password,
                otp_token=otp_token,
                scope=scope,
                expires_in=expires_in
            )
            self.bearer_token = self._token.access_token

        return self.authorized

    @property
    def request_headers(self) -> Dict:
        return {
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}',
        }

    @property
    def authorized(self) -> bool:
        return bool(self.bearer_token)
