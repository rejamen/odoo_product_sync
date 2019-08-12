# -*- coding: utf-8 -*-
{
    'name': "Odoo Product Sync",

    'summary': """
        Sync Odoo products with an external source.""",

    'description': """
        The product synchronisation its done in both ways:
        1.  odoo -> external system
        If the product changes in Odoo it is synchronised to the external system.

        2.  external system -> odoo
        If the product changes in the external system it is possible to get 
        these changes. 

        In product detail view it has been added a widget to check the synchronisation 
        state. If the external product data is different than the Odoo product data 
        it shows “Sync needed”, otherwise it shows “Synced”.
    """,

    'author': "Aidooit",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','connector'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}