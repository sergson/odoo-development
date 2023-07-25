# -*- coding: utf-8 -*-

from openerp import api, fields, models, _

from openerp.exceptions import UserError


class AccountInvoiceInherited(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def unlink(self):
#MY ADD START
        all_users=self.pool.get('res.users')
        cr=self._cr
        uid=self._uid
        if all_users.has_group(cr, uid, 'account.group_account_manager'):
            return super(AccountInvoiceInherited, self).unlink()
#MY ADD END           
        for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            elif invoice.move_name:
                raise UserError(_('You cannot delete an invoice after it has been validated (and received a number). You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        return super(AccountInvoiceInherited, self).unlink()

# MY ADD START
    def invoice_line_move_line_get_dest(self):
        res = []
        for line in self.invoice_line_ids:
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))

            move_line_dict = {
                'invl_id': line.id,
                'type': 'dest',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': -line.price_subtotal,
                'account_id': self.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
            }
            if line['account_analytic_id']:
                move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(move_line_dict)
        return res


    def invoice_line_move_line_get_tax(self):
        res = []
        for line in self.invoice_line_ids:
#            tax_ids = []
#            for tax in line.invoice_line_tax_ids:
#                tax_ids.append((4, tax.id, None))
#                for child in tax.children_tax_ids:
#                    if child.type_tax_use != 'none':
#                        tax_ids.append((4, child.id, None))

            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.tax_amount,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_id': self.id,
            }
            if line['account_analytic_id']:
                move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(move_line_dict)
        return res

    def invoice_line_move_line_get_dest_tax(self):
        res = []
        for line in self.invoice_line_ids:

#            tax_ids = []
#            for tax in line.invoice_line_tax_ids:
#                tax_ids.append((4, tax.id, None))
#                for child in tax.children_tax_ids:
#                    if child.type_tax_use != 'none':
#                        tax_ids.append((4, child.id, None))
            move_line_dict = {
                'invl_id': line.id,
                'type': 'dest',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': -line.tax_amount,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_id': self.id,
            }
            if line['account_analytic_id']:
                move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(move_line_dict)
        return res
# MY ADD END

# MY ADD START
    def tax_line_move_line_get_dest(self):
        res = []
        for tax_line in self.tax_line_ids:
            res.append({
                'tax_line_id': tax_line.tax_id.id,
                'type': 'tax',
                'name': tax_line.name,
                'price_unit': tax_line.amount,
                'quantity': 1,
                'price': -tax_line.amount,
                'account_id': tax_line.tax_id.x_corr_account_id.id or self.account_id.id,
                'account_analytic_id': tax_line.account_analytic_id.id,
            })
        return res
# MY ADD END

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
# MY ADD START
            if inv.payment_term_id:
                iml += inv.invoice_line_move_line_get_tax()
            iml += inv.invoice_line_move_line_get_dest()
            if inv.payment_term_id:
                iml += inv.invoice_line_move_line_get_dest_tax()
# MY ADD END
            iml += inv.tax_line_move_line_get()
# MY ADD START
            iml += inv.tax_line_move_line_get_dest()
# MY ADD END
            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount

            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
#MOD BY ME START
#            if inv.payment_term_id:
#
#                totlines = inv.with_context(ctx).payment_term_id.compute(total, date_invoice)[0]
#                res_amount_currency = total_currency
#                ctx['date'] = date_invoice
#                for i, t in enumerate(totlines):
#                    if inv.currency_id != company_currency:
#                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
#                    else:
#                        amount_currency = False

                    # last line: add the diff
#                    res_amount_currency -= amount_currency or 0
#                    if i + 1 == len(totlines):
#                        amount_currency += res_amount_currency
#
#                    iml.append({
#                        'type': 'dest',
#                        'name': name,
#                        'price': t[1],
#                        'account_id': inv.account_id.id,
#                        'date_maturity': t[0],
#                        'amount_currency': diff_currency and amount_currency,
#                        'currency_id': diff_currency and inv.currency_id.id,
#                        'invoice_id': inv.id
#                    })
#
#
#            else:

#                iml.append({
#                    'type': 'dest',
#                    'name': name,
#                    'price': total,
#                    'account_id': inv.account_id.id,
#                    'date_maturity': inv.date_due,
#                    'amount_currency': diff_currency and total_currency,
#                    'currency_id': diff_currency and inv.currency_id.id,
#                    'invoice_id': inv.id
#                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['dont_create_taxes'] = True
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
# ADD BY ME START
            move.button_cancel()
# ADD BY ME END
        return True

class AccountInvoiceLineInherited(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        # MY ADD
        self.tax_amount = taxes['total_included'] - taxes['total_excluded'] if taxes else 0
        # MY ADD
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    # MY ADD START
    tax_amount = fields.Monetary(string='Amount', store=True, readonly=True, compute='_compute_price')
    # MY ADD END
