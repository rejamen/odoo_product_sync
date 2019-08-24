# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job
from odoo.addons.connector.components.mapper import mapping

import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    """Call create, write and unlink method to create events."""
    @api.model
    def create(self, vals):
    	record = super(product_template, self).create(vals)
    	self._event('on_record_create').notify(record, fields=vals.keys())
    	return record

    
    @api.multi
    def write(self, vals):
    	record = super(product_template, self).write(vals)
    	self._event('on_record_write').notify(record, fields=vals.keys())
    	return record

    
    @api.multi
    def unlink(self):
    	record = super(product_template, self).unlink()
    	self._event('on_record_unlink').notify(record)
    	return record

    
    @job
    @api.multi
    def export_product(self):
    	_logger.info("Exporting data!!!!!!!!!!!")

    
    @api.multi
    def action_export_product(self):
    	self.with_delay().export_product()

    
    sync_state = fields.Selection([
    	('sync_needed', 'Sync needed'),
    	('synced', 'Synced')], 'Sync status', default='sync_needed')


class product_create_event_listener(Component):
    _name = 'product.create.event.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.template']

    
    def on_record_create(self, record, fields=None):
        _logger.info("%r has been created!!!!!!!", record)
        self.map_name(record)
        

    @mapping
    def map_name(self, record):
        return {'name': record.name} 


class product_write_event_listener(Component):
    _name = 'product.write.event.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.template']

    def on_record_write(self, record, fields=None):
        _logger.info("%r has been modified!!!!!!!", record)


class product_unlink_event_listener(Component):
    _name = 'product.unlink.event.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.template']

    def on_record_unlink(self, record, fields=None):
        _logger.info("%r has been deleted!!!!!!!", record)


class ExternalBackend(models.Model):
    _name = 'external.backend'
    _description = 'External Service'
    _inherit = 'connector.backend'

    external_url = fields.Char('URL')
    username = fields.Char()
    password = fields.Char()
    access_token = fields.Char()


class ExternalSourceProduct(models.Model):
    _name = 'external.source.product'
    _inherit = 'external.binding'
    _description = 'External Source Product'

    backend_id = fields.Many2one(
        comodel_name='external.backend',
        string='External Backend',
        required=True,
        ondelete='restrict',
    )
    external_id = fields.Integer(string='ID in the External Source', index=True)

