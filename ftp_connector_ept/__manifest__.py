#!/usr/bin/python3
{
    'name': 'FTP Connector',
    'version': '13.0.2',
    'category': 'Sale',
    'license': 'OPL-1',
    'author': 'Tripode-Services.',
    'website': 'http://www.tripode-services.fr',
    'maintainer': 'Tripode-services.',
    'description': '''
        Make Connection to FTP through odoo
    ''',
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
    'images': ['static/description/FTP-Integration.jpg']
}

