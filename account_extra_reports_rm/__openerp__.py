# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Extra Accounting Reports RU modified',
    'version': '1.0',
    'author': 'Odoo, Serg Terihov',
    'category': 'Accounting & Finance',
    'description': """
Extra Accounting Reports RU modified.
====================================

This module adds two new reports:
* Sale/Purchase Journal (Журнал ордер) 
* Partner Ledger (Акт сверки)
    """,
    'website': 'https://www.odoo.com/page/accounting',
    'depends': ['account_accountant', 'account_ru_mod'],
    'data': [
        'wizard/account_report_print_journal_view.xml',
        'views/report_journal.xml',
        'wizard/account_report_partner_ledger_view.xml',
        'views/report_partnerledger.xml',
        'views/report_generalledger_partner.xml',
        'wizard/account_report_general_ledger_partner_view.xml',
        'data/account_report.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
