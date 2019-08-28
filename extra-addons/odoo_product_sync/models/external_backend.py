# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ExternalBackend(models.Model):
    """Represents the external service to synchronize with.

    It inherits from connector.backend class.
    """
    _name = 'external.backend'
    _inherit = 'connector.backend'
    _description = 'External Service to sync'

    @api.multi
    def test_connection(self):
        """Test connection with external source."""
        for record in self:
            url = record.url
            username = record.username
            password = record.password
            access_token = record.access_token

            access = self.backend_api(url, username, password, access_token)
            if access:
                _logger.info('Successful Connection!!!')
                record.update({
                    'state': 'done',
                })
            else:
                _logger.error('Error in Connection!!!')
                raise UserError('Connection Error.')

    def backend_api(self, url, username, password, token):
        """Access logic to external API.

            It depends on the external service. Basically use
            access credentials to access to the external API.
            Return 'True' if success, else 'False'.
        """
        success = True
        # Do access logic and set success False if error
        return success

    @api.multi
    def change_configuration(self):
        """Allows to change connection parameters."""
        for record in self:
            record.update({'state': 'draft'})

    @api.multi
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
    connector_source = fields.Selection(
        [
            ('magento', 'Magento'),
            ('amazon', 'Amazon'),
            ('ebay', 'Ebay'),
        ], 'External Source', required=True,
        help='Specify external connector source.')
    state = fields.Selection(
        [
            ('draft', 'Untested'),
            ('done', 'Success'),
        ], 'Connection status', default='draft')
