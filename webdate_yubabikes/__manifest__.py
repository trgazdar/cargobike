# -*- coding: utf-8 -*-

{
    # Module Information
    'name': 'Webdate Yubabikes',
    'category': 'Website/eCommerce',
    'summary': 'Gestion des dates de livraison Yubabikes',
    'version': '13.0.0.0',
    "description": """
        Gestion des dates de livraison Yubabikes
    """,
    'license': 'OPL-1',    
    'depends': ['website_sale','stock'],

    'data': [
        'views/res_config_settings.xml',
        'templates/templates.xml',
    ],

    'images': [
        'static/description/stock_qty.png',
    ],

    'author': 'Yoann Guillemot',
    'website': 'http://www.web-erp-consulting.com',

    'installable': True,
    'auto_install': False,
}
