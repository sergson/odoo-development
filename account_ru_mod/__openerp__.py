# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Russian Invoicing modifications',
    'version': '1.0',
    'author': 'Serg Terihov',
    'summary': 'Modifications in unlink, reports, move line creation',
    'sequence': 30,
    'description': """
Invoicing & Payments modifications for Russian accounting
====================
Unlink can been by Administrator user in account.bank.statement, account.bank.statement.line, account.invoice
Providing to creating two line accounting records with two corresponding accounts in one move such as Russian accounting.
Added tax_amount in accounting records.
Replaced property_account_payable_id 'internal_type' to receivable.
Replaced property_account_receivable_id 'internal_type' to payable. 
Setting for account.payment if partner_type == 'employee'. 
Modifications in pdf reports.
Modifications in translations.
    """,
    'category': 'Localization',
    'website': 'https://www.odoo.com',
    'images' : [],
    'depends' : ['base_setup', 'product', 'analytic', 'report', 'web_tip', 'web_planner', 'account'],
    'data': [
        'views/account_view.xml',
        'views/report_agedpartnerbalance_modifed.xml',
        'views/report_generalledger_modified.xml',
        'views/report_overdue_modified.xml',
        'views/report_trialbalance_modifed.xml',
        'wizard/account_report_aged_partner_balance_modifed_view.xml',
        'wizard/account_report_general_ledger_modified_view.xml',
        'wizard/account_report_trial_balance_modified_view.xml',
        'data/account_ru_mod_report.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
