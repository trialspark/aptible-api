from os import environ
from pathlib import Path
from typing import Dict
import json

from .api_manager import ApiManager
from .aptible_auth_api import AptibleAuthApi
from ..config import CONFIG_PATH_ENV_KEY, ACCESS_TOKEN_ENV_KEY


class AptibleApi(ApiManager):
    # pylint: disable=inconsistent-return-statements, too-many-arguments

    def __init__(self, api_url_base: str = "https://api.aptible.com"):
        self._tokens_file = Path('~').expanduser() / '.aptible' / 'tokens.json'
        self._token = None
        self._bearer_token = None
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
            self._bearer_token = token

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
            self._bearer_token = self._token.access_token

        return self.authorized

    def unauthorize(self) -> None:
        self._bearer_token = None

    @property
    def config_path(self) -> Path:
        if CONFIG_PATH_ENV_KEY in environ:
            return environ.get(CONFIG_PATH_ENV_KEY)
        return Path('~').expanduser() / '.aptible'

    @property
    def tokens_file(self) -> Path:
        return self.config_path / 'tokens.json'

    @property
    def bearer_token(self) -> str:
        if self._bearer_token:
            return self._bearer_token

        if ACCESS_TOKEN_ENV_KEY in environ:
            return environ.get(ACCESS_TOKEN_ENV_KEY, '')

        if self.tokens_file.exists():
            tokens_data = json.loads(self.tokens_file.read_text('utf-8'))
            self._bearer_token = tokens_data.get('https://auth.aptible.com', '')
            return self._bearer_token

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
