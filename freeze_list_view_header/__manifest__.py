# -*- coding: utf-8 -*-
{
    'name': "Fixed / Freeze / Sticky List View Header & Footer",
    'summary': """To fixed / freeze / sticky list view's Header & Footer, very helpful when scrolling down with many record.""",
    'description': """
        To fixed / freeze / sticky list view's header & Footer, very helpful when scrolling down with many record.
        To see total amount in footer.
        It supports column resizing new feature in Odoo 13.0.
    """,
    'author': "Tintumon .M",
    'website': "https://tintumon.co.in",
    'category': 'web',
    'version': '13.0.0.1',
    'depends': [
        'web',
    ],
    'data': [
        'views/freeze_list_view_header_view.xml',
    ],
    'images': ['static/description/listview.gif'],
    'price': 10,
    'currency': 'EUR',
    'license': 'OPL-1',
}
