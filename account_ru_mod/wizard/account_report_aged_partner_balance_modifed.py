# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError


class AccountAgedTrialBalanceModified(models.TransientModel):

    _inherit = 'account_ru_mod.common.report'
    _name = 'account_ru_mod.aged.trial.balancemodified'
    _description = 'Account Aged Trial balance Report Modified'

    x_initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.', default=True)
    x_sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    x_account_id = fields.Many2one('account.account', string = 'Номер счета')
    period_length = fields.Integer(string='Period Length (days)', required=False, default=30)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    x_display_account = fields.Selection([('all','All'), ('movement','With movements'),
                                        ('not_zero','With balance is not equal to 0'),],
                                        string='Display Accounts', required=True, default='movement')
    result_selection = fields.Selection([('customer','customer'), ('supplier','supplier')],
                                        string='result_selection', required=False, default='customer')


    @api.multi
    def pre_print_report(self, data):
        data['form'].update(self.read(['x_display_account'])[0])
        return data

    def _print_report(self, data):
        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        if period_length<=0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            res[str(i)] = {
                'name': (i != 0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
 
        data['form'].update(self.read(['x_initial_balance', 'x_sortby'])[0])
        data['form'].update({'x_account_id': self.x_account_id.id})
        if data['form'].get('x_initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
       
        return self.env['report'].with_context(landscape=True).get_action(self, 'account_ru_mod.report_agedpartnerbalance_modified', data=data)
