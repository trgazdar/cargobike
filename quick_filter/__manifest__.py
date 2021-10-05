# -*- coding: utf-8 -*-
# Part of Atharva System. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Parts Finder',
    'category' : 'Website',
    'summary': """
		Add especially valuable for odoo ecommenrce stores selling spare parts and other components.
    """,
    'license' : 'OPL-1',
    'version': '1.0',
    'author': 'Atharva System',
    'website': 'https://www.atharvasystem.com',
    'support': 'support@atharvasystem.com',
    'description': """
        Product Parts Finder,
        Year-Make-Model Product Search,
        YMM Search,
        Year Make Model Search,
        Year make model product finder,
        Odoo year make model filters,
        quickly find parts,
        quick find parts,
        Car Make Model Year Module,
        car parts finder,
        Filter by Year Make Model,
        parts finder,
        Year Make Model Search,
        vehicle part search,
        vehicle parts search, 
        easily part search, 
        part finder,
        advance search,
        Website Advance Search,
        Car Repair Management Odoo,
        Auto Parts Search,Auto Parts Website snippet      
    """,
    'depends' : ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/quick_finder_view.xml',
        'views/product_display_view.xml',
        'views/templates.xml'
    ],
    'images': ['static/description/app_banner.png'],
	'price': 95.00,
    'currency': 'EUR',
    'installable': True,
    'application': True
}
