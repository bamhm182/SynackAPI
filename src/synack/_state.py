"""handler.py

Defines the handler class and generally sets up the project.
"""

import pathlib
import requests

from typing import Union


class State(object):
    def __init__(self):
        self._config_dir = None
        self._debug = None
        self._email = None
        self._http_proxy = None
        self._https_proxy = None
        self._login = None
        self._notifications_token = None
        self._otp_secret = None
        self._password = None
        self._proxies = None
        self._session = None
        self._template_dir = None
        self._use_proxies = None
        self._user_id = None

    @property
    def config_dir(self) -> pathlib.PosixPath:
        if self._config_dir is None:
            self._config_dir = pathlib.Path('~/.config/synack').expanduser().resolve()
        if self._config_dir:
            self._config_dir.mkdir(parents=True, exist_ok=True)
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if type(value) == str:
            value = pathlib.Path(value).expanduser().resolve()
        self._config_dir = value

    @property
    def template_dir(self) -> pathlib.PosixPath:
        ret = self._template_dir
        if ret:
            ret.mkdir(parents=True, exist_ok=True)
        return ret

    @template_dir.setter
    def template_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if type(value) == str:
            value = pathlib.Path(value).expanduser().resolve()
        self._template_dir = value

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
        return self._session

    @property
    def login(self) -> bool:
        return self._login

    @login.setter
    def login(self, value: bool) -> None:
        self._login = value

    @property
    def use_proxies(self) -> bool:
        return self._use_proxies

    @use_proxies.setter
    def use_proxies(self, value: bool) -> None:
        self._use_proxies = value

    @property
    def http_proxy(self) -> str:
        return self._http_proxy

    @http_proxy.setter
    def http_proxy(self, value: str) -> None:
        self._http_proxy = value

    @property
    def https_proxy(self) -> str:
        return self._https_proxy

    @https_proxy.setter
    def https_proxy(self, value: str) -> None:
        self._https_proxy = value

    @property
    def proxies(self) -> dict():
        return {
            'http': self.http_proxy,
            'https': self.https_proxy
        }

    @property
    def otp_secret(self) -> str:
        return self._otp_secret

    @otp_secret.setter
    def otp_secret(self, value: str) -> None:
        self._otp_secret = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @property
    def user_id(self) -> str:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value
