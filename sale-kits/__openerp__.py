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
    'name': 'Sale kits',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Sale kits add kits menu in sale order form.
===========================================================
Module give a possibility to create any kind of sale order lines kits and save it. 
""",
    'author': 'Serg Terihov',
    'website': '',
	'price': '10',
	'currency': 'EUR',
    'depends': ['sale'],
	'images': ['images/sale-kits.pgn'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_kits_wizard_view.xml',
        'views/sale_kits_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
