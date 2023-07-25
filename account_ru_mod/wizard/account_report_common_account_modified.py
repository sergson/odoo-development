# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class AccountCommonAccountReportModified(models.TransientModel):
    _inherit = "account_ru_mod.common.report"
    _name = 'account_ru_mod.common.account_report'
    _description = 'Account Common Account Report Modified'
    
    display_account = fields.Selection([('all','All'), ('movement','With movements'), 
                                        ('not_zero','With balance is not equal to 0'),], 
                                        string='Display Accounts', required=True, default='movement')

    @api.multi
    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        return data
