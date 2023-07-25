﻿# -*- coding: utf-8 -*-
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
    'name': 'Russia - Documents modified',
    'version': '2.2',
    'summary': 'Первичные документы',
    'description': """
The module for print documents in accordance laws of Russia.
============================================================
Возможности:
    * Товарная накладная (ТОРГ-12)
    * Счет на оплату
    * Счет-фактура
    * Акт выполненных работ
    * Вывод подписей и печати
    """,
    'author': 'CodUP, Serg Terihov',
    'website': 'http://codup.com',
    'images': ['static/description/docs.png'],
    'category': 'Localization',
    'sequence': 0,
    'depends': ['sale'],
    'demo': ['l10n_ru_doc_demo.xml'],
    'data': [
        'account_invoice_view.xml',
        'res_partner_view.xml',
        'res_company_view.xml',
        'res_users_view.xml',
        'res_bank_view.xml',
        'l10n_ru_doc_data.xml',
        'report/l10n_ru_doc_report.xml',
        'report/report_order.xml',
        'report/report_invoice.xml',
        'report/report_bill.xml',
        'report/report_act.xml',
        'report/report_act_rent.xml',
        'report/report_act_acceptance_rent.xml',
        'report/report_act_acceptance_work.xml',
        'report/report_act_no_items.xml',
        'edi/bill_action_data.xml',
    ],
    'css': ['static/src/css/l10n_ru_doc.css'],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
