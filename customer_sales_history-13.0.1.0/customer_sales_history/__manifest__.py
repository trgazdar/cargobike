# -*- encoding: utf-8 -*-
##############################################################################
#
# Craftsync Technologies
# Copyright (C) 2020(https://www.craftsync.com)
#
##############################################################################

{
    'name': "Customer Sales History",
    'category': 'Sales',
    'version': '1.0',
    'author': 'Craftsync Technologies',
    'maintainer': 'Craftsync Technologies',
    'website': 'https://www.craftsync.com',
    'summary': """
        View Customer sales history from customer and sales order view.""",
    'author': "Craftsync Technologies",
    'description': """
        This module will help to view customer product sales history from
        customer and sales order view using smart button.
    """,
    'depends': ['sale_management'],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml'
        ],
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'demo': [],
    'images': ['static/description/main_screen.png'],
    'price': 19.99,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
}
