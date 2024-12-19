from datetime import datetime, time
from typing import Callable, Dict
from urllib.parse import urlencode

import pytz
import requests
from requests import Request

from shipay_modules_wallets.logger_type import L
from shipay_modules_wallets.providers import PspTimezone
from shipay_modules_wallets.providers.exceptions import PSPProviderException, PSPProviderTimeoutException
from shipay_modules_wallets.providers.psps.pix import Pix
from shipay_modules_wallets.schemas.pix import PixQueryParams


class Pix(Pix):
    def __init__(self, wallet_data: dict, timeout_config: Dict, logger: L, save_auth: Callable = None,
                 async_class: bool = False,  timezone: PspTimezone = PspTimezone.BRT,
                 **kwargs):
        self.timezone = timezone
        super().__init__(wallet_data=wallet_data, timeout_config=timeout_config, logger=logger,
                         async_class=async_class, save_auth=save_auth, **kwargs)

    def __str__(self):
        return 'Pix '

    def __new__(cls, wallet_data, timeout_config: Dict, logger: L, save_auth: Callable = None,
                async_class: bool = False, **kwargs):

        return object.__new__(cls)

    def _auth(self):
        request_attrs = {
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'data': {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        }

        self._set_attributes_payload(request_attrs)

        url = f'{self.auth_url}/api/oauth/token'
        self.logger.info(f'[{self.tracking_id}][Pix] Requesting {url}')

        try:

            with self._mtls_request(self.tls_cert, self.tls_key, self.mtls) as cert:
                if cert:
                    request_attrs.update({'cert': cert, 'verify': True})

                _auth = requests.post(url, **request_attrs, timeout=self.timeout_config.get('auth'))

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            self.logger.exception(f'[Pix][Itau] Timeout of {self.timeout_config.get("auth")} while attempting to '
                                  f'authenticate to the payment service provider reached.')
            raise PSPProviderTimeoutException('Timeout when trying to authenticate with payment service provider '
                                              'reached.')
