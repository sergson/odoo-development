# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory Management russian documents',
    'version': '1',
    'summary': 'Inventory, Logistics, Warehousing',
    'description': """
Inventory Management russian documents
==============================================================
Added ability to remove pack operations.
Added some report of pack operations.

    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['stock',
                'sale',
                'purchase',
                'hr_expense',
                'l10n_ru_doc'],
    'category': 'Warehouse',
    'author': 'Serg Terihov',
    'sequence': 13,
    'demo': [],
    'data': [
        'views/report_stock_order.xml',
        'stock_report.xml'
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
