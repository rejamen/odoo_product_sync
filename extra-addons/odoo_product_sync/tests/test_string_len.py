# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class MyTest(TransactionCase):
    def test_string_trim(self):
        self.assertEqual(len('Hola mundo'), 50)
