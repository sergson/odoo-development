# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Purchase Management order remove ability',
    'version': '1',
    'category': 'Purchases',
    'sequence': 60,
    'summary': 'Purchase Order line remove',
    'description': """
Purchase Management order remove ability
==================================================
Added the ability to remove Purchase Management lines and orders
Added the ability to cancel orders in the "done" state  
    """,
    'website': 'https://www.odoo.com/page/purchase',
    'author': 'Serg Terihov',
    'depends': ['purchase'],
    'data': ['purchase_view.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
