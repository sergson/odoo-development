# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv

class stock_pickingRuMod(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'expense_run_id': fields.related('move_lines', 'expense_id', 'expinse_run_id', string="Expense",
            readonly=True, relation="many2one"),
    }


class stock_moveRuMod(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'expense_id': fields.many2one('hr.expense',
            'Expense', ondelete='set null', select=True,
            readonly=True),
    }
