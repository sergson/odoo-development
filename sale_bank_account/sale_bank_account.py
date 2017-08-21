# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class SaleOrderBankAccount(models.Model):
    _inherit = "sale.order"

    @api.multi
    def default_company_bank_account(self):
        default_bank_account_id=self.env['ir.values'].get_default('sale.config.settings', 'default_bank_account')
        bank_account=self.env['res.partner.bank'].browse(default_bank_account_id)
        if not default_bank_account_id or not bank_account:
            return self.env['res.partner.bank'].search([], limit=1)
        return bank_account

    company_bank_account = fields.Many2one('res.partner.bank', 'Company bank account', ondelete='set null', default=default_company_bank_account, help='Select company bank account for this sale order' )
    partner_bank_account = fields.Many2one('res.partner.bank', 'Partner bank account', ondelete='set null', help='Select partner bank account for this sale order')

    @api.multi
    @api.onchange('partner_id')
    def default_partner_bank_account(self):
        if not self.partner_id:
            self.update({
                'partner_bank_account': False
            })
            return
        bank_account_ids=self.env['res.partner.bank'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        if not bank_account_ids:
            self.update({
                'partner_bank_account': False
            })
            return
        self.update({
                'partner_bank_account': bank_account_ids
            })


#    @api.multi
#    @api.onchange('partner_id')
#    def default_company_bank_account(self):
#        if not self.company_id:
#            self.update({
#                'company_bank_account': False
#            })
#            return
#        bank_account_ids=self.env['ir.values'].get_default('sale.config.settings', 'default_bank_account')
#        if not bank_account_ids:
#            self.update({
#                'company_bank_account': False
#            })
#            return
#        self.update({
#                'company_bank_account': self.env['res.partner.bank'].browse(bank_account_ids)
#            })


