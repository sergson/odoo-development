# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime

PRICE_TOLERANCE = 0.05  # Tolerance for manual price variation

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    validity_date = fields.Date(string='Expiration Date', readonly=True,
                                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': u'По договору (контракту) №{0} от {1} на {2}'.format(self.contract_number, datetime.strptime(self.contract_date,"%Y-%m-%d").strftime("%d.%m.%Y"), self.note) if self.contract_number else self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals

    @api.onchange('pricelist_id')
    def pricelist_id_change(self):
        lang_val = self.partner_id.lang
        partner_val = self.partner_id.id
        date_val = self.date_order
        pricelist_val = self.pricelist_id.id
        vals = {}
        mod_lines = []
        for line in self.order_line:
            product = line.product_id.with_context(
                lang=lang_val,
                partner=partner_val,
                quantity=line.product_uom_qty,
                date=date_val,
                pricelist=pricelist_val,
                uom=line.product_uom.id
            )
            line_vals = {}
            ctrl_price = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
            line_vals['price_unit'] = ctrl_price
            price = line_vals['price_unit'] * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)
            line_vals['price_tax'] = taxes['total_included'] - taxes['total_excluded']
            line_vals['price_total'] = taxes['total_included']
            line_vals['price_subtotal'] = taxes['total_excluded']
            mod_lines.append([1, line.id, line_vals])
        if len(mod_lines) > 0:
            vals['order_line'] = mod_lines
        self.update(vals)

    @api.multi
    def unlink(self):
        all_users = self.pool.get('res.users')
        cr = self._cr
        uid = self._uid
        context = None
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'sale.group_sale_manager'
        admins = ['Administrator']
        if not(user_name in admins or all_users.has_group(cr, uid, managers_group)):
            raise UserError(_('Cannot delete a sale order without some permissions'))
        for order in self:
            if order.state != 'draft':
                raise UserError(_('You can only delete draft quotations!'))
        return super(SaleOrderInherit, self).unlink()

    @api.multi
    def action_back(self):
        self.write({'state': 'sale'})




class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('price_unit')
    def price_unit_change(self):
        lang_val = self.order_id.partner_id.lang
        partner_val = self.order_id.partner_id.id
        date_val = self.order_id.date_order
        pricelist_val = self.order_id.pricelist_id.id
        product = self.product_id.with_context(
            lang=lang_val,
            partner=partner_val,
            quantity=self.product_uom_qty,
            date=date_val,
            pricelist=pricelist_val,
            uom=self.product_uom.id
        )
        line_vals = {}
        ctrl_price = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, self.tax_id)
        if abs(self.price_unit - ctrl_price) > PRICE_TOLERANCE * ctrl_price:
            line_vals['price_unit'] = ctrl_price
            price = line_vals['price_unit'] * (1 - (self.discount or 0.0) / 100.0)
        else:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.tax_id.compute_all(price, self.order_id.currency_id, self.product_uom_qty,
                                        product=self.product_id, partner=self.order_id.partner_id)
        line_vals['price_tax'] = taxes['total_included'] - taxes['total_excluded']
        line_vals['price_total'] = taxes['total_included']
        line_vals['price_subtotal'] = taxes['total_excluded']
        self.update(line_vals)

    @api.multi
    def unlink(self):
        if self.filtered(lambda x: x.state in ('done')):
            raise UserError(_('You can not remove a sale order line.\nDiscard changes and try setting the quantity to 0.'))
        return super(SaleOrderLineInherit, self).unlink()

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
            if not self.product_id:
                return {'domain': {'product_uom': []}}

            vals = {}
            domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
            if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
                vals['product_uom'] = self.product_id.uom_id
                vals['product_uom_qty'] = 1.0

            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id
            )
            # MOD BY ME ST
            if self.product_id:
                curent_pricelist_item = self.env['product.pricelist.item'].search(
                    [('product_id', '=', self.product_id.id), ('pricelist_id', '=', self.order_id.pricelist_id.id)],
                    limit=1)
            #            _logger.debug('PLITEM'+str(curent_pricelist_item))

            name = product.name_get()[0][1]
            if product.description_sale:
                name += '\n' + product.description_sale
            vals['name'] = name

            self._compute_tax_id()

            if self.order_id.pricelist_id and self.order_id.partner_id:
                vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id,
                                                                                     self.tax_id)
                # ADD BY ME
                vals['product_uom_qty'] = curent_pricelist_item.min_quantity
            # ADD BY ME
            self.update(vals)
            return {'domain': domain}

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date_order=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )

            if self.product_id:
                curent_pricelist_item = self.env['product.pricelist.item'].search(
                    [('product_id', '=', self.product_id.id), ('pricelist_id', '=', self.order_id.pricelist_id.id)],
                    limit=1)
                old_product_uom_qty = self.env['sale.order.line'].browse([self._origin.id]).product_uom_qty
                product_uom_qty = self.product_uom_qty
                if all([old_product_uom_qty,
                       self.order_id.state in ['sale', 'done', 'cancel'],
                       self.product_uom_qty != old_product_uom_qty]):
                    product_uom_qty = old_product_uom_qty
                product_uom_factor = self.env['product.uom'].browse([self.product_uom.id]).factor
                product_base_uom_factor = curent_pricelist_item.product_id.product_tmpl_id.uom_id.factor
                min_qty = curent_pricelist_item.min_quantity

                if product_base_uom_factor:
                    min_qty_line_units = min_qty / product_base_uom_factor * product_uom_factor
                else:
                    min_qty_line_units = min_qty

                if min_qty > 0 and product_uom_qty < min_qty_line_units:
                    product_uom_qty = min_qty_line_units
                vals = {}
                vals['product_uom_qty'] = product_uom_qty
                self.update(vals)

            self.price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id,
                                                                              self.tax_id)