# -*- encoding: utf-8 -*-
{
    'name': 'Import Multiline Bank Statement 1c',
    'category' : 'Accounting & Finance',
    'version': '0.1',
    'author': 'krzem.ru (Serg Terihov)',
    'description' : """
Module to import Multiline bank statements 1c format.
======================================

This module allows you to import the machine readable Multiline TXT Files 1c in Odoo.
    
    """,
    'data': ['account_bank_statement_import_1c_view.xml'],
    'depends': ['account_bank_statement_import'],
    'demo': [],
    'auto_install': True,
    'installable': True,
}
