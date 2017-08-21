# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
from openerp.exceptions import AccessError

class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'
    
    @api.multi
    def _default_bank_account(self):
        partner = self.env.user.company_id.partner_id
        bank_account_ids=self.env['res.partner.bank'].search([('partner_id', '=', partner.id)], limit=1)
        if bank_account_ids:
            return bank_account_ids

    default_bank_account = fields.Many2one('res.partner.bank', 'Bank account', ondelete='set null', default=_default_bank_account, help='Select bank account for sale orders by default')
    
    @api.multi
    @api.onchange('default_bank_account')
    def onchange_default_bank_account(self):
        res={}
        partner = self.env.user.company_id.partner_id
        res['domain'] = {'default_bank_account':[('partner_id', '=', partner.id)]}
        return res  

    def set_bank_account_defaults(self, cr, uid, ids, context=None):
        default_bank_account=self.browse(cr, uid, ids, context=context).default_bank_account
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'default_bank_account', default_bank_account.id)
        return res
