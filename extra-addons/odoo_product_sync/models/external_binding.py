# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.component.core import AbstractComponent
from odoo.addons.component.core import Component

class ExternalBackend(models.Model):
    """Model for external source."""
    _name = 'external.backend'
    _inherit = 'connector.backend'
    _description = 'External Source to sync'

    #custom fields of external source
    name = fields.Char()
    url = fields.Char('URL')

    def import_product(self, external_id):
        """Import product from external source."""
        with self.work_on(model_name='external.product.product') as work:
            importer = work.component(usage='record.importer')
            # return an instance of ProductImporter, which has been
            # found with: the collection name (external.backend, the model,
            # and the usage).
            importer.run(external_id)


class BaseExternalConnectorComponent(AbstractComponent):
    """ Base External Connector Component.

    All components of this connector sould inherit from it.
    """
    _name = 'base.external.connector'
    _inherit = 'base.connector'
    _collection = 'external.backend'


class ExternalModelBinder(Component):
    """Bind records and give Odoo/external ids correspondence.

    Binding models are model called external.{normal_model},
    for example, por Odoo products would be: external.product.product.
    They are _inherits of the normal models and contains the external ID,
    the ID of the Backend and the additional fields belonging to the
    external instance.
    """
    _name = 'external.binder'
    _inherit = ['base.binder', 'base.external.connector']
    _apply_on = [
        'external.product.product',
        ]


class ExternalProductProduct(models.Model):
    """Binding between Odoo model and external record."""
    _name = 'external.product.product'
    _inherit = 'external.binding'
    _inherits = {'product.product': 'odoo_id'}
    _description = 'External Product'

    odoo_id = fields.Many2one('product.product', 'Product',
                                required=True,
                                ondelete='restricted')
    backend_id = fields.Many2one('external.backend', 'External Backend',
                                    required=True,
                                    ondelete='restrict')
    external_id = fields.Char('ID in external source')
    sync_date = fields.Date('Sync date', help='Last date of synchronization')
