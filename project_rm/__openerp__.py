# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project task change security',
    'version': '1',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project Management',
    'sequence': 10,
    'summary': 'Projects, Tasks',
    'depends': ['project'],
    'description': """
Project task change security
=====================================================
Checking if user not an admin or project manager to prevent changes in task values by user
    """,
    'author': 'Serg Terihov',
    'data': [],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
