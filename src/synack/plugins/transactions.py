"""plugins/transactions.py

Functions dealing with payouts/money
"""

import json

from .base import Plugin


class Transactions(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Auth']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def get_balance(self):
        """Get your current account balance and requested payout values"""
        res = self._api.request('HEAD', 'transactions')
        if res.status_code == 200:
            return json.loads(res.headers.get('x-balance'))
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()
