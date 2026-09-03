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
        self.state._db = MagicMock()
        self.transactions = synack.plugins.Transactions(self.state)
        self.transactions._api = MagicMock()

    def test_get_balance(self):
        """Should get the balance of your synack account"""
        bal = b'''{
            "total_balance": "10.0",
            "pending_payout": "0.0"
        }'''
        self.transactions._api.request.return_value.headers = {'x-balance': bal}
        self.transactions._api.request.return_value.status_code = 200
        ret = self.transactions.get_balance()
        self.assertEqual(ret, json.loads(bal))
        self.transactions._api.request.assert_called_with('HEAD',
                                                          'transactions')

    def test_get_balance_403_login(self):
        """Should call get_api_token on 403 when login is True"""
        self.transactions._auth = MagicMock()
        self.transactions._api.request.return_value.status_code = 403
        self.state.login = True
        self.transactions.get_balance()
        self.transactions._auth.get_api_token.assert_called_once()

    def test_get(self):
        """Should return a single page of transactions"""
        txns = [{'id': 1}, {'id': 2}]
        self.transactions._api.request.return_value.status_code = 200
        self.transactions._api.request.return_value.json.return_value = txns
        ret = self.transactions.get(period='2024', per_page=15)
        self.assertEqual(ret, txns)
        self.transactions._api.request.assert_called_with(
            'GET', 'transactions',
            query={'period': '2024', 'per_page': 15, 'page': 1})

    def test_get_paginates(self):
        """Should follow pagination while a full page is returned"""
        page1 = [{'id': 0}, {'id': 1}]
        page2 = [{'id': 99}]
        self.transactions._api.request.return_value.status_code = 200
        self.transactions._api.request.return_value.json.side_effect = [page1, page2]
        ret = self.transactions.get(per_page=2, max_pages=2)
        self.assertEqual(ret, [{'id': 0}, {'id': 1}, {'id': 99}])

    def test_get_403_login(self):
        """Should call get_api_token on 403 when login is True"""
        self.transactions._auth = MagicMock()
        self.transactions._api.request.return_value.status_code = 403
        self.state.login = True
        self.assertEqual(self.transactions.get(), [])
        self.transactions._auth.get_api_token.assert_called_once()

    def test_get_non_200(self):
        """Should return an empty list on a non-200/403 response"""
        self.transactions._api.request.return_value.status_code = 500
        self.assertEqual(self.transactions.get(), [])
