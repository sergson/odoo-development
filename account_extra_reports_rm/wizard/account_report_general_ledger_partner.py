# -*- coding: utf-8 -*-

from openerp import fields, models, _
from openerp.exceptions import UserError


class AccountReportGeneralLedgerPartner(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = "account.report.general.ledger.partner"
    _description = "General Ledger Partner Report"

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.', default=True)
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal', 'account_report_general_ledger_partner_journal_rel', 'account_id', 'journal_id', string='Journals', required=True)
#ADD BY ME START
    x_account_id = fields.Many2one('account.account', string = 'Номер счета')
    partner = fields.Many2one('res.partner', string = 'Контрагент')


    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        data['form'].update({'x_account_id': self.x_account_id.id})
        data['form'].update({'partner': self.partner.id})
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        return self.env['report'].with_context(landscape=True).get_action(self, 'account_extra_reports_rm.report_generalledger_partner', data=data)
