# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)


#----------------------------------------------------------
# Quants
#----------------------------------------------------------

class stock_quant_rm(osv.osv):
    _inherit = "stock.quant"

    def _account_entry_move(self, cr, uid, quants, move, context=None):
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation entries for. Unempty and all quants are supposed to have the same location id (thay already moved in)
        move: Move to use. browse record
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(cr, uid, location_to, context=context)

        if move.product_id.valuation != 'real_time':
            return False
        for q in quants:
            if q.owner_id:
                #if the quant isn't owned by the company, we don't make any valuation entry
                return False
            if q.qty <= 0:
                #we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
                #At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
                #to make the adjustments when we know the real cost price.
                return False

        #in case of routes making the link between several warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # Create Journal Entry for products arriving in the company
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_to.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
#MOD START
            if location_from and location_from.usage == 'customer' and acc_dest and acc_valuation:
               #goods returned from customer
                self._create_account_move_line(cr, uid, quants, move, acc_dest, acc_valuation, journal_id, context=ctx)
            elif acc_src and acc_valuation:
                self._create_account_move_line(cr, uid, quants, move, acc_src, acc_valuation, journal_id, context=ctx)
#MOD END
        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('internal', 'transit') or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_from.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
#MOD START
            if location_to and location_to.usage == 'supplier' and acc_valuation and acc_src:
                 #goods returned to supplier
                 self._create_account_move_line(cr, uid, quants, move, acc_valuation, acc_src, journal_id, context=ctx)
            elif acc_valuation and acc_dest:
                 self._create_account_move_line(cr, uid, quants, move, acc_valuation, acc_dest, journal_id, context=ctx)
#MOD END
        if move.company_id.anglo_saxon_accounting and move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'customer':
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            ctx = context.copy()
            ctx['force_company'] = move.company_id.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            self._create_account_move_line(cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)


    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: openerp.exceptions.UserError if any mandatory account or journal is not defined.
        """
        product_obj = self.pool.get('product.template')
        accounts = product_obj.browse(cr, uid, move.product_id.product_tmpl_id.id, context).get_product_accounts()
        if move.location_id.valuation_out_account_id:
            acc_src = move.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts['stock_input'].id

        if move.location_dest_id.valuation_in_account_id:
            acc_dest = move.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts['stock_output'].id

        acc_valuation = accounts.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
#MOD START
#        if not accounts.get('stock_journal', False):
#            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts'))
#        if not acc_src:
#            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (move.product_id.name))
#        if not acc_dest:
#            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (move.product_id.name))
#        if not acc_valuation:
#            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
#MOD END
        journal_id = accounts['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation

    def _create_account_move_line(self, cr, uid, quants, move, credit_account_id, debit_account_id, journal_id, context=None):
        #group quants by cost
        quant_cost_qty = {}
        for quant in quants:
            if quant_cost_qty.get(quant.cost):
                quant_cost_qty[quant.cost] += quant.qty
            else:
                quant_cost_qty[quant.cost] = quant.qty
        move_obj = self.pool.get('account.move')
        for cost, qty in quant_cost_qty.items():
            move_lines = self._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
            if move_lines:
#MOD START
#                date = context.get('force_period_date', fields.date.context_today(self, cr, uid, context=context))
                date = context.get('force_period_date', move.picking_id.min_date or fields.date.context_today(self, cr, uid, context=context))
#MOD END
                new_move = move_obj.create(cr, uid, {'journal_id': journal_id,
                                          'line_ids': move_lines,
                                          'date': date,
                                          'ref': move.picking_id.name}, context=context)
                move_obj.post(cr, uid, [new_move], context=context)

    #def _reconcile_single_negative_quant(self, cr, uid, to_solve_quant, quant, quant_neg, qty, context=None):
    #    move = self._get_latest_move(cr, uid, to_solve_quant, context=context)
    #    quant_neg_position = quant_neg.negative_dest_location_id.usage
    #    remaining_solving_quant, remaining_to_solve_quant = super(stock_quant, self)._reconcile_single_negative_quant(cr, uid, to_solve_quant, quant, quant_neg, qty, context=context)
    #    #update the standard price of the product, only if we would have done it if we'd have had enough stock at first, which means
    #    #1) there isn't any negative quant anymore
    #    #2) the product cost's method is 'real'
    #    #3) we just fixed a negative quant caused by an outgoing shipment
    #    if not remaining_to_solve_quant and move.product_id.cost_method == 'real' and quant_neg_position != 'internal':
    #        self.pool.get('stock.move')._store_average_cost_price(cr, uid, move, context=context)
    #    return remaining_solving_quant, remaining_to_solve_quant
