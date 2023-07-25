# -*- coding: utf-8 -*-

from openerp import fields, api, models, _
from openerp.exceptions import UserError

class AccountReportGeneralLedgerModified(models.TransientModel):
    _inherit = "account_ru_mod.common.account_report"
    _name = "account_ru_mod.report.general.ledger_modified"


    x_account_id = fields.Many2one('account.account', string = 'Номер счета')

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                     help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by',
                              required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal', 'account_report_general_ledger_modified_journal_rel', 'account_id',
                                   'journal_id', string='Journals', required=True)

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        data['form'].update({'x_account_id': self.x_account_id.id})
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        #records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=True).get_action(self, 'account_ru_mod.report_generalledger_modified', data=data)