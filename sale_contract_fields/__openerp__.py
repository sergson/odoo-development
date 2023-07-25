# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2015 CodUP (<http://codup.com>).
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
    'name': 'Sale contract fields',
    'version': '0.1',
    'summary': 'Дополнительные поля для договора',
    'description': """
The module for print contract in accordance laws of Russia.
============================================================
Возможности:
    * В модель res.partner, res.use добавляется поля для заполнения договора
    """,
    'author': 'Serg Terihov',
    'website': '',
    'category': 'Localization',
    'sequence': 0,
    'depends': ['sale'],
    'demo': ['l10n_ru_doc_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'sale_contract_fields.xml',
    ],
    'installable': True,
}
