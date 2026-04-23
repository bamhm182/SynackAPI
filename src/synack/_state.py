"""handler.py

Defines the handler class and generally sets up the project.
"""

import pathlib
import requests

from typing import Union


class State(object):
    def __init__(self):
        self._api_token = None
        self._config_dir = None
        self._db = None
        self._debug = None
        self._email = None
        self._http_proxy = None
        self._https_proxy = None
        self._login = None
        self._notifications_token = None
        self._otp_secret = None
        self._otp_count = None
        self._password = None
        self._proxies = None
        self._scratchspace_dir = None
        self._session = None
        self._slack_app_token = None
        self._slack_channel = None
        self._slack_url = None
        self._smtp_email_from = None
        self._smtp_email_to = None
        self._smtp_password = None
        self._smtp_port = None
        self._smtp_server = None
        self._smtp_starttls = None
        self._smtp_username = None
        self._synack_domain = None
        self._template_dir = None
        self._use_proxies = None
        self._use_scratchspace = None
        self._user_id = None

    @property
    def smtp_email_from(self) -> str:
        ret = self._smtp_email_from
        if ret is None:
            ret = self._db.smtp_email_from
        return ret

    @smtp_email_from.setter
    def smtp_email_from(self, value: str) -> None:
        self._smtp_email_from = value

    @property
    def smtp_email_to(self) -> str:
        ret = self._smtp_email_to
        if ret is None:
            ret = self._db.smtp_email_to
        return ret

    @smtp_email_to.setter
    def smtp_email_to(self, value: str) -> None:
        self._smtp_email_to = value

    @property
    def smtp_password(self) -> str:
        ret = self._smtp_password
        if ret is None:
            ret = self._db.smtp_password
        return ret

    @smtp_password.setter
    def smtp_password(self, value: str) -> None:
        self._smtp_password = value

    @property
    def smtp_port(self) -> str:
        ret = self._smtp_port
        if ret is None:
            ret = self._db.smtp_port
        return ret

    @smtp_port.setter
    def smtp_port(self, value: str) -> None:
        self._smtp_port = value

    @property
    def smtp_server(self) -> str:
        ret = self._smtp_server
        if ret is None:
            ret = self._db.smtp_server
        return ret

    @smtp_server.setter
    def smtp_server(self, value: str) -> None:
        self._smtp_server = value

    @property
    def smtp_starttls(self) -> str:
        ret = self._smtp_starttls
        if ret is None:
            ret = self._db.smtp_starttls
        return ret

    @smtp_starttls.setter
    def smtp_starttls(self, value: str) -> None:
        self._smtp_starttls = value

    @property
    def smtp_username(self) -> str:
        ret = self._smtp_username
        if ret is None:
            ret = self._db.smtp_username
        return ret

    @smtp_username.setter
    def smtp_username(self, value: str) -> None:
        self._smtp_username = value

    @property
    def api_token(self) -> str:
        ret = self._api_token
        if ret is None:
            ret = self._db.api_token
        return ret

    @api_token.setter
    def api_token(self, value: str) -> None:
        self._api_token = value

    @property
    def config_dir(self) -> pathlib.PosixPath:
        if self._config_dir is None:
            self._config_dir = pathlib.Path('~/.config/synack').expanduser().resolve()
        if self._config_dir:
            self._config_dir.mkdir(parents=True, exist_ok=True)
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if isinstance(value, str):
            value = pathlib.Path(value).expanduser().resolve()
        self._config_dir = value

    @property
    def synack_domain(self):
        ret = self._synack_domain
        if ret is None:
            ret = self._db.synack_domain
        return ret

    @synack_domain.setter
    def synack_domain(self, value):
        self._synack_domain = value

    @property
    def template_dir(self) -> pathlib.PosixPath:
        ret = self._template_dir
        if ret is None:
            ret = self._db.template_dir
        ret.mkdir(parents=True, exist_ok=True)
        return ret

    @template_dir.setter
    def template_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if isinstance(value, str):
            value = pathlib.Path(value).expanduser().resolve()
        self._template_dir = value

    @property
    def scratchspace_dir(self) -> pathlib.PosixPath:
        ret = self._scratchspace_dir
        if ret is None:
            ret = self._db.scratchspace_dir
        ret.mkdir(parents=True, exist_ok=True)
        return ret

    @scratchspace_dir.setter
    def scratchspace_dir(self, value: Union[str, pathlib.PosixPath]) -> None:
        if isinstance(value, str):
            value = pathlib.Path(value).expanduser().resolve()
        self._scratchspace_dir = value

    @property
    def debug(self) -> bool:
        ret = self._debug
        if ret is None:
            ret = self._db.debug
        return ret

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
    def notifications_token(self) -> str:
        ret = self._notifications_token
        if ret is None:
            ret = self._db.notifications_token
        return ret

    @notifications_token.setter
    def notifications_token(self, value: str) -> None:
        self._notifications_token = value

    @property
    def use_proxies(self) -> bool:
        ret = self._use_proxies
        if ret is None:
            ret = self._db.use_proxies
        return ret

    @use_proxies.setter
    def use_proxies(self, value: bool) -> None:
        self._use_proxies = value

    @property
    def use_scratchspace(self) -> bool:
        ret = self._use_scratchspace
        if ret is None:
            ret = self._db.use_scratchspace
        return ret

    @use_scratchspace.setter
    def use_scratchspace(self, value: bool) -> None:
        self._use_scratchspace = value

    @property
    def http_proxy(self) -> str:
        ret = self._http_proxy
        if ret is None:
            ret = self._db.http_proxy
        return ret

    @http_proxy.setter
    def http_proxy(self, value: str) -> None:
        self._http_proxy = value

    @property
    def https_proxy(self) -> str:
        ret = self._https_proxy
        if ret is None:
            ret = self._db.https_proxy
        return ret

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
        ret = self._otp_secret
        if ret is None:
            ret = self._db.otp_secret
        return ret

    @otp_secret.setter
    def otp_secret(self, value: str) -> None:
        self._otp_secret = value

    @property
    def otp_count(self) -> str:
        ret = self._otp_count
        if ret is None:
            ret = self._db.otp_count
        return ret

    @otp_count.setter
    def otp_count(self, value: int) -> None:
        self._otp_count = value

    @property
    def email(self) -> str:
        ret = self._email
        if ret is None:
            ret = self._db.email
        return ret

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def slack_app_token(self) -> str:
        ret = self._slack_app_token
        if ret is None:
            ret = self._db.slack_app_token
        return ret

    @slack_app_token.setter
    def slack_app_token(self, value: str) -> None:
        self._slack_app_token = value

    @property
    def slack_channel(self) -> str:
        ret = self._slack_channel
        if ret is None:
            ret = self._db.slack_channel
        return ret

    @slack_channel.setter
    def slack_channel(self, value: str) -> None:
        self._slack_channel = value

    @property
    def slack_url(self) -> str:
        ret = self._slack_url
        if ret is None:
            ret = self._db.slack_url
        return ret

    @slack_url.setter
    def slack_url(self, value: str) -> None:
        self._slack_url = value

    @property
    def password(self) -> str:
        ret = self._password
        if ret is None:
            ret = self._db.password
        return ret

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @property
    def user_id(self) -> str:
        ret = self._user_id
        if ret is None:
            ret = self._db.user_id
        return ret

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value
