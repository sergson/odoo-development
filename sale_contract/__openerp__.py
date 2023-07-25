# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2015 CodUP (<http://codup.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



{
    'name': 'Sale contract and documents',
    'version': '1.0',
    'summary': 'Sale order additional wizard',
    'description': """
Sale contract and documents add document menu in sale order form.
===========================================================
Module give a possibility to create any kind of document, save and print it through Qweb report. 
There are document temlates saving avaible. You may save templates from document and reload it 
to another document. Module gives flaxible tuning of document content by using any html expressions. 
Idea based on python format function using to get any value of sale order or sale order 
line or related fields value to you document. 
Document in this modile consist of any numbers of document conditions with any you want content 
with html format. In document conditions form you may see some fields to choose model, model fields, 
python code qweb text and report view. Help popups can explain format text for good job.
""",
    'author': 'Serg Terihov',
    'website': '',
    'depends': ['sale', 'sale_timesheet', 'product_expiry', 'sale_order_dates'],
    'category': 'Sale',
    'sequence': 0,
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/document_template_wizard_view.xml',
        'views/sale_contract_view.xml',
        'report/sale_contract_report.xml',
        'report/sale_contract_doc_report.xml',
    ],
    'installable': True,
}
