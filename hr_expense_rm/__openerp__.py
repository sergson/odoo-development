# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Russian Expense Tracker',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 95,
    'summary': 'Modifications for Expenses Validation, Invoicing',
    'description': """
Modifications for Manage expenses by Employees
==============================================
    
Russian advance report added.

    """,
    'author': 'Serg Terihov',
    'website': 'https://www.odoo.com',
    'depends': ['hr_contract', 'account_accountant', 'report', 'hr_expense', 'stock', 'l10n_ru_doc'],
    'data': ['views/hr_expense_views.xml',
             'views/report_expense_run.xml',
             'views/hr_expense_report.xml'],
    'demo': [],
    'installable': True,
    'application': True,
}
