# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Courier tasks',
    'version': '1.0',
    'category': 'Extra Tools',
    'author': 'Serg Terihov',
    'price': '10',
    'currency': 'EUR',
    'summary': 'Courier tasks',
    'description': """
Manage courier tasks
============================

This application allows you create couriers and manage a list of tasks for them.
Couriers can check any task to done after have finishing.
Users and managers can give tasks, courier can only done tasks.
After task have saved email message woud be send to courier emain.
Courier email set thouth couriers menu by manager. 

    """,
    'website': '',
    'depends': ['base', 'mail', 'report'],
    'data': [
        'security/courier_tasks_security.xml',
        'security/ir.model.access.csv',
        'views/courier_tasks_view.xml',
        'data/email_template_data.xml'
    ],
    'installable': True,
    'application': True,
}
