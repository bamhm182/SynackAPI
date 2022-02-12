"""test_transactions.py

Tests for the Transactions Plugin
"""

import json
import os
import sys
import unittest


from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class TransactionsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.transactions = synack.plugins.Transactions(self.state)
        self.transactions.api = MagicMock()

    def test_get_balance(self):
        """Should get the balance of your synack account"""
        bal = b'''{
            "total_balance": "10.0",
            "pending_payout": "0.0"
        }'''
        self.transactions.api.request.return_value.headers = {'x-balance': bal}
        self.transactions.api.request.return_value.status_code = 200
        ret = self.transactions.get_balance()
        self.assertEqual(ret, json.loads(bal))
        self.transactions.api.request.assert_called_with('HEAD',
                                                         'transactions')
