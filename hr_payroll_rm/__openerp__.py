#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll Modifications for Russian accounting',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 38,
    'description': """
Payroll Modifications for Russian accounting.
=============================================

Pay slip form adding
Payroll form adding
    """,
    'author': 'Serg Terihov'
    'website': 'https://www.odoo.com/page/employees',
    'depends': [
        'hr_payroll',
        'hr_payroll_account'
    ],
    'data': [
        'hr_payroll_view.xml',
        'hr_payroll_report.xml',
        'views/report_payslip.xml',
        'views/report_payslip_run.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
