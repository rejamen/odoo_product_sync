# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.component.core import Component

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    """Inherits product.template class to add custom logic."""
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        """Triggering an event on create record."""
        record = super(ProductTemplate, self).create(vals)
        self._event('on_record_create').notify(record, fields=vals.keys())
        return record

    @api.multi
    def write(self, vals):
        """Triggering an event on write record."""
        record = super(ProductTemplate, self).write(vals)
        self._event('on_record_write').notify(record, fields=vals.keys())
        return record

    @api.multi
    def unlink(self):
        """Triggering an event on unlink record."""
        record = super(ProductTemplate, self).unlink()
        self._event('on_record_unlink').notify(record)
        return record

    # add sync state for widget
    sync_state = fields.Selection([
        ('sync_needed', 'Sync needed'),
        ('synced', 'Synced')], 'Sync status', default='sync_needed')
    # other fields related to external source
    external_bind_ids = fields.One2many(
        comodel_name='external.product.product',
        inverse_name='odoo_id',
        string='External Bindings')


class ProductTemplateEventListener(Component):
    _name = 'product.template.event.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.template']

    def on_record_create(self, record, fields=None):
        """Listening to event on record create."""
        _logger.info("%r has been created!!!!!!!", record)

    def on_record_write(self, record, fields=None):
        """Listening to event on record write."""
        _logger.info("%r has been modified!!!!!!!", record)

    def on_record_unlink(self, record, fields=None):
        """Listening to event on record unlink."""
        _logger.info("%r has been deleted!!!!!!!", record)
