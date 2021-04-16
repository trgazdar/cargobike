{
    # App information
    'name': "FTP EDI Integration in Odoo",
    'category': 'Stock',
    'version': '13.0',
    'summary': 'Odoo  EDI Integration helps orders to carriers by FTP,'
               ' products & inventory via EDI Integration through FTP server.',
    'license': 'OPL-1',

    # Author
    "author": "Tripode-Services.fr",
    'website': 'http://www.tripode-services.fr',
    'maintainer': 'Tripode-Services',

    # Dependencies
    'depends': ['sale', 'stock', 'delivery', 'purchase', 'stock_dropshipping', 'ftp_connector_ept',
                'common_connector_library'],

    # View
    'data': ['data/ir_cron.xml',
             'view/ftp_server_ept_view.xml',
             'view/res_partner_view.xml',
             'view/active_suppliers_ept_view.xml',
             'view/dropship_product_ept_view.xml',
             'view/common_log_book_ept_view.xml',
             'view/product_template_view.xml',
             'view/stock_picking_view.xml',
             'view/stock_picking_type_view.xml',
             'wizard/dropship_operation_wizard.xml',
             'security/ir.model.access.csv',
             ],

    'images': ['static/description/Tripode-Services-LOGO.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
