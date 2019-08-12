# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_template(models.Model):
    _inherit = 'product.template'

    sync_state = fields.Selection([
    	('sync_need', 'Sync needed'),
    	('synced', 'Synced')], 'Sync status')
