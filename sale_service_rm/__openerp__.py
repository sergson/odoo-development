# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Create Tasks from SO by product attribute time',
    'version': '1.0',
    'category': 'Project',
    'description': """
Automatically creates project tasks from procurement lines by product attribute time.
=====================================================================================
If you create product attribute time, the task will created by product time and quantum
""",
    'website': 'https://www.odoo.com/page/crm',
    'author': 'Serg Terihov',
    'depends': ['sale_service'],
    'data': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
