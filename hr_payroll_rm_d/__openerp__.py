#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll Modifications for Russian accounting data',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 38,
    'description': """
Payroll Modifications for Russian accounting data.
=============================================
Salary structure data adding
    """,
    'website': 'https://www.odoo.com/page/employees',
    'author': 'Serg Terihov',
    'depends': [
        'hr_payroll',
        'hr_payroll_account',
        'hr_payroll_rm',
    ],
    'data': [
        'hr_payroll_data.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
