# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)

import openerp.addons.decimal_precision as dp

class HrExpenseRuMod(models.Model):

    _inherit = "hr.expense"

    name = fields.Many2one('hr.expense.doc', string='Документ', readonly=True, required=True, states={'draft': [('readonly', False)]})
    x_partner_id = fields.Many2one('res.partner', string='Поставщик',  domain=[('supplier', '=', True)],  required=True, readonly=True, states={'draft': [('readonly', False)]})
    x_doc_number = fields.Char(srting='Номер документа',  required=True, readonly=True, states={'draft': [('readonly', False)]})
    expense_run_id = fields.Many2one('hr.expense.run', 'Авансовые отчеты', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    x_num_of_lists = fields.Integer(string='Количество листов', required=True, readonly=True, states={'draft': [('readonly', False)]}, default = 1)
    procurement_ids = fields.One2many('procurement.order', 'expense_id', string='Associated Procurements', copy=False)
    move_ids = fields.One2many('stock.move', 'expense_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    expense_run_date = fields.Date(string='Дата авансового отчета', related='expense_run_id.date', readonly=True)


    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        for expense in self:
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id, expense.employee_id.user_id.partner_id)
            expense.total_amount = taxes.get('total_included')
            expense.untaxed_amount = taxes.get('total_excluded')


    @api.multi
    def unlink(self):

        all_users=self.pool.get('res.users')
        cr=self._cr
        uid=self._uid
        if all_users.has_group(cr, uid, 'account.group_account_manager'):
            return super(HrExpenseRuMod, self).unlink()
        elif any(expense.state not in ['draft', 'cancel'] for expense in self):
            raise UserError(_('You can only delete draft or refused expenses!'))
        return super(HrExpenseRuMod, self).unlink()

    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': line['partner_id'],
            'name': line['name'][:64],
            'date': self.expense_run_id.date,
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or -abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'ref': line.get('ref'),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
        }

    @api.multi
    def action_move_create(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        if any(expense.state != 'approve' for expense in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(expense.employee_id != self[0].employee_id for expense in self):
            raise UserError(_("Expenses must belong to the same Employee."))

        if any(not expense.journal_id for expense in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        journal_dict = {}
        maxdate = False
        for expense in self:
            if expense.date > maxdate:
                maxdate = expense.date
            jrn = expense.bank_journal_id if expense.payment_mode == 'company_account' else expense.journal_id
            journal_dict.setdefault(jrn, [])
            journal_dict[jrn].append(expense)

        for journal, expense_list in journal_dict.items():
            #create the move that will contain the accounting entries
            move = self.env['account.move'].create({
                'journal_id': journal.id,
                'company_id': self.env.user.company_id.id,
                'date': maxdate,
            })
            for expense in expense_list:
                company_currency = expense.company_id.currency_id
                diff_currency_p = expense.currency_id != company_currency
                #one account.move.line per expense (+taxes..)
                move_lines = expense._move_line_get()

                #create one more move line, a counterline for the total on payable account
                total, total_currency, move_lines = expense._compute_expense_totals(company_currency, move_lines, maxdate)
                if expense.payment_mode == 'company_account':
                    if not expense.bank_journal_id.default_credit_account_id:
                        raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.bank_journal_id.name))
                    emp_account = expense.bank_journal_id.default_credit_account_id.id
                else:
                    if not expense.employee_id.address_home_id:
                        raise UserError(_("No Home Address found for the employee %s, please configure one.") % (expense.employee_id.name))
                    emp_account = expense.employee_id.address_home_id.property_account_payable_id.id


                move_lines_total = []
                for line in move_lines:    
                    move_lines_total.append({
                            'type': 'dest',
                            'name': expense.x_partner_id.name,
                            'price': -line['price'],
                            'account_id': emp_account,
                            'date_maturity': expense.expense_run_id.date,
                            'amount_currency': diff_currency_p and total_currency or False,
                            'currency_id': diff_currency_p and expense.currency_id.id or False,
                            'ref': expense.expense_run_id.name or False,
                            'partner_id': expense.expense_run_id.employee_id.address_home_id.commercial_partner_id.id or expense.employee_id.address_home_id.commercial_partner_id.id
                            })
                for line in move_lines_total:
                    move_lines.append(line)

                #convert eml into an osv-valid format
                lines = map(lambda x:(0, 0, expense._prepare_move_line(x)), move_lines)
                move.with_context(dont_create_taxes=True).write({'line_ids': lines}) #move.write({'line_ids': lines})
                expense.write({'account_move_id': move.id, 'state': 'post'})
                if expense.payment_mode == 'company_account':
                    expense.paid_expenses()
            if move.line_ids:
                move.post()
            else:
                move.unlink()
        return True

    @api.multi
    def _move_line_get(self):
        account_move = []
        for expense in self:
            if expense.total_amount == 0:
                return account_move
            if expense.product_id:
                account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
                if not account:
                    raise UserError(
                        _("No Expense account found for the product %s (or for it's category), please configure one.") % (
                            expense.product_id.name))
            else:
                account = self.env['ir.property'].with_context(force_company=expense.company_id.id).get(
                    'property_account_expense_categ_id', 'product.category')
                if not account:
                    raise UserError(
                        _('Please configure Default Expense account for Product expense: `property_account_expense_categ_id`.'))
            move_line = {
                'type': 'src',
                'name': expense.product_id.name.split('\n')[0][:64],
                'price_unit': expense.unit_amount,
                'quantity': expense.quantity,
                'price': expense.untaxed_amount,
                'account_id': account.id,
                'product_id': expense.product_id.id,
                'uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'partner_id': expense.x_partner_id.id,
            }
            account_move.append(move_line)

            # Calculate tax lines and adjust base line
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity,
                                                expense.product_id)
            account_move[-1]['price'] = taxes['total_excluded']
            account_move[-1]['tax_ids'] = [(6, 0, expense.tax_ids.ids)]
            for tax in taxes['taxes']:
                account_move.append({
                    'type': 'tax',
                    'name': tax['name'],
                    'price_unit': tax['amount'],
                    'quantity': 1,
                    'price': tax['amount'],
                    'account_id': tax['account_id'] or move_line['account_id'],
                    'tax_line_id': tax['id'],
                    'partner_id': expense.x_partner_id.id,
                })
        return account_move

    @api.multi
    def _create_stock_moves(self, picking, partner_id):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self.filtered(lambda r: r.x_partner_id in partner_id):
            order = line.expense_run_id
            taxes = line.tax_ids.compute_all(line.unit_amount, line.currency_id, 1, line.product_id,
                                             line.employee_id.user_id.partner_id)
            price_unit = taxes.get('total_excluded')
            if line.product_uom_id.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom_id.factor / line.product_id.uom_id.factor
            if line.currency_id != line.company_id.currency_id:
                price_unit = line.currency_id.compute(price_unit, line.company_id.currency_id, round=False)

            template = {
                'name': line.x_partner_id.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'date': line.expense_run_id.date,
                'date_expected': line.expense_run_id.date,
                'location_id': line.x_partner_id.property_stock_supplier.id,
                'location_dest_id': line.expense_run_id._get_destination_location(),
                'picking_id': picking.id,
                'partner_id': line.expense_run_id.employee_id.address_home_id.commercial_partner_id.id or line.employee_id.address_home_id.commercial_partner_id.id,
                'move_dest_id': False,
                'state': 'draft',
                'expense_id': line.id,
                'company_id': line.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.expense_run_id.picking_type_id.id,
                'group_id': False,
                'procurement_id': False,
                'origin': line.expense_run_id.name,
                'route_ids': line.expense_run_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in line.expense_run_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': line.expense_run_id.picking_type_id.warehouse_id.id,
            }
            # Fullfill all related procurements with this po line
            diff_quantity = line.quantity
            for procurement in line.procurement_ids:
                procurement_qty = procurement.product_uom._compute_qty_obj(procurement.product_uom, procurement.product_qty, line.product_uom_id)

                tmp = template.copy()
                tmp.update({
                    'product_uom_qty': min(procurement_qty, diff_quantity),
                    'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement dest$
                    'procurement_id': procurement.id,
                    'propagate': procurement.rule_id.propagate,
                })
                done += moves.create(tmp)
                diff_quantity -= min(procurement_qty, diff_quantity)
            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom_id.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done




class HrExpenseRun(models.Model):

    _name = "hr.expense.run"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Авансовый отчет"
    _order = "date desc"

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    @api.depends('expense_ids.move_ids.picking_id')
    def _compute_picking(self):
        for order in self:
            pickings = self.env['stock.picking']
            for line in order.expense_ids:
                moves = line.move_ids.filtered(lambda r: r.state != 'cancel')
                pickings |= moves.mapped('picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    name = fields.Char(string='Номер авансового отчета', readonly=True, required=True, states={'draft': [('readonly', False)]})
    date = fields.Date(readonly=True, required=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today, string="дата")
    state = fields.Selection([('draft', 'Draft'),
                              ('close', 'Close'),
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='draft', required=True)
    expense_ids = fields.One2many('hr.expense', 'expense_run_id', 'Expense', required=False, readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string="Подотчетное лицо", required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    prepayment_type = fields.Many2one('hr.expense.type', string = "Назначение аванса",required=True, readonly=True, states={'draft': [('readonly', False)]})
    prev_prepayment = fields.Float(string='Предыдущий аванс', readonly=True, states={'draft': [('readonly', False)]}, digits=dp.get_precision('Product Price'))
    prepayment = fields.Many2many('account.move', string='Получен аванс', readonly=True, states={'draft': [('readonly', False)]})
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=READONLY_STATES, required=True, default=_default_picking_type,\
        help="This will determine picking type of incoming shipment")
    dest_address_id = fields.Many2one('res.partner', string='Drop Ship Address', states=READONLY_STATES,\
        help="Put an address if you want to deliver directly from the vendor to the customer. "\
             "Otherwise, keep empty to deliver to your own company.")
    group_id = fields.Many2one('procurement.group', string="Procurement Group")


    @api.multi
    def draft_expense_run(self):
        for pick in self.picking_ids:
            if pick.state == 'done':
                raise UserError(_('Невозможно отменить складскую перацию %s, так как она уже выполнена.') % (pick.name))

        for pick in self.picking_ids.filtered(lambda r: r.state != 'cancel'):
            pick.action_cancel()
        return self.write({'state': 'draft'})

    @api.multi
    def close_expense_run(self):
        self._create_picking()
        self.write({'state': 'close'})
        return {}

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.dest_address_id:
            return self.dest_address_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id


    @api.model
    def _prepare_picking(self, partner_id):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.employee_id.address_home_id.commercial_partner_id.id or self.employee_id.address_home_id.commercial_partner_id.id,
            })

        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': partner_id.id,
            'date': self.date,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': partner_id.property_stock_supplier.id
        }

    @api.multi
    def _create_picking(self):
        self.ensure_one()
        expense = 0
        for expense in self.expense_ids.mapped('x_partner_id'):
            if any([ptype in ['product', 'consu'] for ptype in self.expense_ids.filtered(lambda r: r.x_partner_id in expense).mapped('product_id.type')]):
                res = self._prepare_picking(expense)
                picking = self.env['stock.picking'].create(res)
                moves = self.expense_ids.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking, expense)
                moves.action_confirm()
                moves.force_assign()
        return True

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result['context'] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result


class ProcurementOrderRuMod(models.Model):
    _inherit = 'procurement.order'

    expense_id = fields.Many2one('hr.expense', string='Expense')
    expense_run_id = fields.Many2one(related='expense_id.expense_run_id', string='Expense run')


class HrExpenseDocRuMod(models.Model):

    _name = "hr.expense.doc"
    _description = "Наименование документа"

    name = fields.Char(string='Наименование документа', required=True)

class HrExpenseTypeRuMod(models.Model):

    _name = "hr.expense.type"
    _description = "Назначение аванса"

    name = fields.Char(string='Назначение аванса', required=True)