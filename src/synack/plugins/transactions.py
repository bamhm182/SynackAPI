"""plugins/transactions.py

Functions dealing with payouts/money
"""

import json


class Transactions:
    def __init__(self, handler):
        self.handler = handler

    def get_balance(self):
        """Get your current account balance and requested payout values"""
        res = self.handler.api.request('HEAD', 'transactions')
        if res.status_code == 200:
            return json.loads(res.headers.get('x-balance'))
