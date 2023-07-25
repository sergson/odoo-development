# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountCommonJournalReportModified(models.TransientModel):
    _inherit = "account_ru_mod.common.report"
    _name = 'account.common.journal_report_mod'
    _description = 'Account Common Journal Report'

    amount_currency = fields.Boolean('With Currency', help="Print Report with the currency column if the currency differs from the company currency.")

    @api.multi
    def pre_print_report(self, data):
        data['form'].update({'amount_currency': self.amount_currency})
        return data
