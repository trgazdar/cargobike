{
    # App information
    'name': "Dropshipping EDI Integration in Odoo",
    'category': 'Purchases',
    'version': '13.0',
    'summary': 'Odoo Dropshipping EDI Integration helps dropshipper to manage orders,'
               ' products & inventory via EDI Integration through FTP server.',
    'license': 'OPL-1',

    # Author
    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

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

    'images': ['static/description/Dropshipping-EDI-Integration.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.emiprotechnologies.com/free-trial?app=dropship-edi-integration-ept&version=13&edition=enterprise',
    'currency': 'EUR',
    'price': '699',
}
