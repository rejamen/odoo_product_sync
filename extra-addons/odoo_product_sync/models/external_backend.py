# -*- coding: utf-8 -*-

from odoo import models, fields

import logging
_logger = logging.getLogger(__name__)


class ExternalBackend(models.Model):
    """Represents the external service to synchronize with.

    It inherits from connector.backend class.
    """
    _name = 'external.backend'
    _inherit = 'connector.backend'
    _description = 'External Service to sync'

    def test_connection(self):
        """Test connection with external source."""
        # TODO
        _logger.info('Successful Connection!')
        self.state = 'done'

    def change_configuration(self):
        """Allows to change connection parameters."""
        self.state = 'draft'

    def import_product(self, external_id):
        """Import product from external source."""
        with self.work_on(model_name='external.product.product') as work:
            importer = work.component(usage='record.importer')
            # return an instance of ProductImporter, which has been
            # found with: the collection name (external.backend, the model,
            # and the usage).
            importer.run(external_id)

    name = fields.Char(required=True)
    url = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    access_token = fields.Char(required=True)
    connector_source = fields.Selection([
        ('magento', 'Magento'),
        ('amazon', 'Amazon'),
        ('ebay', 'Ebay')
        ], 'External Source', required=True,
        help='Specify external connector. Depends on that other options can appear.')
    state = fields.Selection([
        ('draft', 'Untested'),
        ('done', 'Success'),
        ], 'Connection status', default='draft')
