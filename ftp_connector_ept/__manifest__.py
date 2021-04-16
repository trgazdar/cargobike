#!/usr/bin/python3
{
    'name': 'FTP Connector',
    'version': '13.0.2',
    'category': 'Sale',
    'license': 'OPL-1',
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'description': '''
        Make Connection to FTP through odoo
    ''',
    'website': 'http://www.emiprotechnologies.com',
    'depends':  ['stock'],
    'external_dependencies': {'python': ['paramiko']},
    'data': [
        'security/ir.model.access.csv',
        'views/ftp_server_view.xml',
        'views/res_config_settings.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'price': 20.00,
    'currency': 'EUR',
    'images': ['static/description/FTP-Integration.jpg']
}

