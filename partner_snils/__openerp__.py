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
    'name': 'Partner SNILS',
    'version': '0.1',
    'summary': 'СНИЛС и паспорт контрагента',
    'description': """
The module for print documents in accordance laws of Russia.
============================================================
Возможности:
    * В модель res.partner добавляется поле для СНИЛС и документа удостоверяющего личность
    """,
    'author': 'Serg Terihov',
    'website': '',
    'category': 'Localization',
    'sequence': 0,
    'depends': ['sale'],
    'demo': ['l10n_ru_doc_demo.xml'],
    'data': [
        'res_partner_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
