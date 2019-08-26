# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.queue_job.job import job


import logging
_logger = logging.getLogger(__name__)

class ExternalConnector(models.Model):
    _name = 'external.connector'

    def test_connection(self):
        """Test connection with external source."""
        _logger.info('Successful Connection!')
        self.state = 'done'


    def change_configuration(self):
        """Allows to change connection parameters."""
        self.state = 'draft'


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
