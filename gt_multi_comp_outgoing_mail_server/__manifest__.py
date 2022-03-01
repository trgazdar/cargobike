# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'SMTP by Company',
    'version': '1.0.0.1',
    'category': 'View',
    'sequence': 1,
    'author': 'Globalteckz',
    'website': 'http://www.globalteckz.com',
    'summary': 'configure multi outgoing mail servers specific to the company',
    "price": "29.00",
    "currency": "EUR",
    'images': ['static/description/BANNER.jpg'],
    "license" : "Other proprietary",
    'description': """

You can configure multi outgoing mail server's specific to the company. 
=========================
outgoing email
smtp
smtp by user
smtp by company
SMTP BY USER OR COMPANY
SMTP BY COMPANY
smtp multicompany
smtp multi company
outgoing email for company
Configure outgoing emails for per company
outgoing emails for per company
outgoing emails each company
outgoing company
different emails
different outgoing email
different outgoing email for company

    """,
    'depends': ['mail','base'],
    'data': [
        'views/ir_mail_server_form.xml',
            ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'qweb': [
            'static/src/xml/thread.xml',
            ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
