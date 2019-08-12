# -*- coding: utf-8 -*-
from odoo import http

# class OdooProductSync(http.Controller):
#     @http.route('/odoo_product_sync/odoo_product_sync/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_product_sync/odoo_product_sync/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_product_sync.listing', {
#             'root': '/odoo_product_sync/odoo_product_sync',
#             'objects': http.request.env['odoo_product_sync.odoo_product_sync'].search([]),
#         })

#     @http.route('/odoo_product_sync/odoo_product_sync/objects/<model("odoo_product_sync.odoo_product_sync"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_product_sync.object', {
#             'object': obj
#         })