# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class AccountBalanceReportModified(models.TransientModel):
    _inherit = "account_ru_mod.common.account_report"
    _name = 'account_ru_mod.balance.report_modified'
    _description = 'Trial balance report modified'

    journal_ids = fields.Many2many('account.journal', 'account_balance_report_journal_rel', 'account_id', 'journal_id', string='Journals', required=True, default=[])

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'account_ru_mod.report_trialbalance_modified', data=data)

