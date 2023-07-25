# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cash report RU',
    'version': '1',
    'category': 'Account',
    'sequence': 20,
    'summary': 'Russian cash report',
    'description': """
Add russian cash report
===========================
    """,
    'author': 'Serg Terihov',
    'depends': ['account_bank_statement_import'],
    'data': ['account_statement_report.xml',
        'report/x_cash_orders_report.xml',
        'report/report_statement.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'qweb': [],
    'website': 'https://www.odoo.com/',
    'auto_install': False,
}
