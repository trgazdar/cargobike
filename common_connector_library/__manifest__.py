# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Common Connector Library',
    'version': '13.0.20',
    'category': 'Sale',
    'license': 'OPL-1',
    'author': 'Tripode-Services.',
    'maintainer': 'Tripode-Services.',
    'description': """Develope Generalize Method Of Sale Order,
                      Sale Order Line which is use in any Connector
                      to Create Sale Order and Sale Order Line.""",
    'depends': ['delivery', 'sale_stock','account_tax_python'],
    'data': ['security/ir.model.access.csv', 'view/stock_quant_package_view.xml',
             'view/common_log_book_view.xml',
             'view/account_fiscal_position.xml',
             'view/common_product_brand_view.xml',
             'view/common_product_image_ept.xml',
             'view/product_view.xml',
             'view/product_template.xml',
             'data/ir_sequence.xml',
             'data/decimal_precision.xml',
             'data/ir_cron.xml',
             'security/res_groups.xml',
             'view/global_channel_ept.xml',
             'view/sale_order_view.xml',
             'view/stock_picking.xml',
             'view/stock_move_view.xml',
             'view/account_move.xml',
             'view/account_move_line_view.xml'],
    'installable': True,
    'images': ['static/description/Common-Connector-Library-Cover.jpg']
}
