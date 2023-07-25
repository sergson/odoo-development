# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountPrintJournalModified(models.TransientModel):
    _inherit = "account.common.journal_report_mod"
    _name = "account.print.journal_mod"
    _description = "Account Print Journal"

    sort_selection = fields.Selection([('date', 'Date'), ('move_name', 'Journal Entry Number'),], 'Entries Sorted by', required=True, default='move_name')
#    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([('type', 'in', ['sale', 'purchase'])]))
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([]))

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'sort_selection': self.sort_selection})
        return self.env['report'].with_context(landscape=True).get_action(self, 'account_extra_reports_rm.report_journal_mod', data=data)
