# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import UserError

class stock_move_inh(osv.osv):
    _inherit = "stock.move"


    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the moves and if all moves are cancelled it cancels the picking.
        @return: True
        """
        all_users = self.pool.get('res.users')
        context = None
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'sale.group_stock_manager'
        admins = ['Administrator']

        procurement_obj = self.pool.get('procurement.order')
        context = context or {}
        procs_to_check = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == 'done':
                if not (user_name in admins or all_users.has_group(cr, uid, managers_group)):
                    raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
            if move.reserved_quant_ids:
                self.pool.get("stock.quant").quants_unreserve(cr, uid, move, context=context)
            if context.get('cancel_procurement'):
                if move.propagate:
                    procurement_ids = procurement_obj.search(cr, uid, [('move_dest_id', '=', move.id)], context=context)
                    procurement_obj.cancel(cr, uid, procurement_ids, context=context)
            else:
                if move.move_dest_id:
                    if move.propagate:
                        if move.move_dest_id.state not in ('done', 'cancel'):
                            self.action_cancel(cr, uid, [move.move_dest_id.id], context=context)
                    elif move.move_dest_id.state == 'waiting':
                        #If waiting, the chain will be broken and we are not sure if we can still wait for it (=> could take from stock instead)
                        self.write(cr, uid, [move.move_dest_id.id], {'state': 'confirmed'}, context=context)
                if move.procurement_id:
                    # Does the same as procurement check, only eliminating a refresh
                    procs_to_check.add(move.procurement_id.id)

        res = self.write(cr, uid, ids, {'state': 'cancel', 'move_dest_id': False}, context=context)
        if procs_to_check:
            procurement_obj.check(cr, uid, list(procs_to_check), context=context)
        return res


class stock_pack_operation_inh(osv.osv):
    _inherit = "stock.pack.operation"

    def unlink(self, cr, uid, ids, context=None):
        all_users = self.pool.get('res.users')
        context = None
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'sale.group_stock_manager'
        admins = ['Administrator']
        if any([x.state in 'cancel' for x in self.browse(cr, uid, ids, context=context)]):
            if not (user_name in admins or all_users.has_group(cr, uid, managers_group)):
                raise UserError(_('You can not delete pack operations of a cancel picking no permitions'))
        if any([x.state in 'done' for x in self.browse(cr, uid, ids, context=context)]):
            raise UserError(_('You can not delete pack operations of a cancel picking no permitions'))
        return super(stock_pack_operation_inh, self).unlink(cr, uid, ids, context=context)
