# -*- coding: utf-8 -*-
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import TransactionCase, tagged
from odoo.addons.connector.exception import InvalidDataError


@tagged('post_install', '-at_install')
class TestImportProduct(TransactionCase):

    def setUp(self):
        super(TestImportProduct, self).setUp()

    def test_import_product(self):
        """ Import of a simple product """
        backend_id = self.backend.id

        product_model = self.env['external.product.product']
        product = product_model.search([('backend_id', '=', backend_id),
                                        ('external_id', '=', '337')])
        self.assertEqual(len(product), 1)

    def test_import_product_configurable(self):
        """ Import of a configurable product : no need to import it

        The 'configurable' part of the product does not need to be imported,
        we import only the variants
        """
        backend_id = self.backend.id

        self.env['external.product.product'].import_record(
            self.backend, '408'
        )

        product_model = self.env['external.product.product']
        products = product_model.search([('backend_id', '=', backend_id),
                                         ('external_id', '=', '408')])
        self.assertEqual(len(products), 0)

    def test_import_product_bundle(self):
        """ Bundle should fail: not yet supported """
        with self.assertRaises(InvalidDataError):
            self.env['external.product.product'].import_record(
                self.backend, '447'
            )

    def test_import_product_grouped(self):
        """ Grouped should fail: not yet supported """
        with self.assertRaises(InvalidDataError):
            self.env['external.product.product'].import_record(
                self.backend, '555'
            )

    def test_import_product_virtual(self):
        """ Virtual products are created as service products """
        backend_id = self.backend.id

        self.env['external.product.product'].import_record(
            self.backend, '563'
        )

        product_model = self.env['external.product.product']
        product = product_model.search([('backend_id', '=', backend_id),
                                        ('external_id', '=', '563')])
        self.assertEqual(product.type, 'service')
