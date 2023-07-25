# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountingCommonPartnerReport(models.TransientModel):
    _inherit = "account_ru_mod.common.report"
    _name = 'account.common.partner_report'
    _description = 'Account Common Partner Report'
    
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                        ('supplier', 'Payable Accounts'),
                                        ('customer_supplier', 'Receivable and Payable Accounts')
                                      ], string="Partner's", required=True, default='customer')

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        return data
