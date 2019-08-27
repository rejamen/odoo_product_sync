# -*- coding: utf-8 -*-

import xmlrpc

from odoo import api, fields, models
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.queue_job.job import job, related_action


class ConnectorBinding(models.AbstractModel):
    """Abstract Model for Bindings in the connector.

    All models used as binding between odoo and external source
    should _inherit it.
    """
    _name = 'connector.binding'
    _description = 'Connector Binding (Abstract)'
    _inherit = 'external.binding'

    # odoo_id field will be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='external.backend',
        string='External Backend',
        required=True,
        ondelete='restrict')
    external_id = fields.Char('ID in external source')


class ExternalProductProduct(models.Model):
    """Binding between Odoo model (product.product) and external record.

    Model name will change for more descriptive one in future
    implementations, like magento.product.product, or
    ebay.product.product.
    """
    _name = 'external.product.product'
    _inherit = 'connector.binding'
    _inherits = {'product.product': 'odoo_id'}
    _description = 'External Product'

    odoo_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        ondelete='cascade')
    sync_date = fields.Date('Sync date', help='Last date of synchronization.')
    # add fields of Products in the external source.
    created_at = fields.Date('Created at (on External source)')
    updated_at = fields.Date('Created at (on External source)')
    product_type = fields.Selection([
        ('simple', 'Simple Product'),
        ('virtual', 'Virtual Product'),
        ('downloadable', 'Downloadable Product'),
        ('giftcard', 'Giftcard')],
        string='Product type (on external source)')
    external_qty = fields.Float('Computed Quantity')

    @job
    @related_action(action='related_action_unwrap_binding')
    @api.multi
    def export_products(self, fields=None):
        """Export products .
        TODO
        """


class ExternalProductAdapter(Component):
    """Adapter for Products in external system.

    It _inherit from GenericAdapter and extends needed functions.
    """
    _name = 'external.product.adapter'
    _inherit = 'generic.adapter'
    _apply_on = 'external.product.product'
    # lets say that Products model name in external system is
    # catalog_product like in Magento (it could be different depends
    # on the external system)
    _external_model = 'catalog_product'

    def _call(self, method, arguments):
        try:
            return super(ExternalProductAdapter, self)._call(method, arguments)
        except xmlrpc.Fault as err:
            # the error in external API
            # when the product does not exist
            if err.faultCode == 101:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        if filters is None:
            filters = {}
        DATETIME_FORMAT = '%Y-%m-%d %H:%M%S'
        if from_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(DATETIME_FORMAT)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(DATETIME_FORMAT)
        # it should be an entry point in the external API
        return [int(row['product_id']) for row
                in self._call('%s.list' % self._external_model,
                              [filters] if filters else [{}])]


class ProductImportMapper(Component):
    """Import Mapper for Products.

    It _inherit Generic Import Mapper module.
    """
    _name = 'product.import.mapper'
    _inherit = 'generic.import.mapper'
    _apply_on = ['external.product.product']

    # direct Mapping ('external_field', 'odoo_field')
    # add more depends on the external source
    direct = [
        ('name', 'name'),
        ('description', 'description'),
        ('cost', 'standard_price'),
        ('sku', 'default_code'),
    ]

    @mapping
    def is_active(self, record):
        """Check if the product is active in the external source and
        set active flag on Odoo. Lets asume that status == 1 in
        external means active."""
        return {'active': (record.get('status') == '1')}

    @mapping
    def price(self, record):
        return {'list_price': record.get('price', 0.0)}

    @mapping
    def type(self, record):
        """Set product type depending on external.

        Assuming product type in external service as simple, virtual,
        downloadable or giftcard (like in Magento) it sets the
        product type in Odoo.
        """
        if record['type_id'] == 'simple':
            return {'type': 'product'}
        elif record['type_id'] in ('virtual', 'downloadable', 'giftcard'):
            return {'type': 'service'}
        return

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}


class ProductImporter(Component):
    _name = 'external.product.importer'
    _inherit = 'generic.importer'
    _apply_on = ['external.product.product']
