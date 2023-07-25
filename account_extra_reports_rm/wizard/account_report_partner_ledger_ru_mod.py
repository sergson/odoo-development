# -*- coding: utf-8 -*-

from openerp import fields, models, _
from openerp.exceptions import UserError


class AccountPartnerLedgerModified(models.TransientModel):
    _inherit = "account.common.partner_report"
    _name = "account.report.partner.ledger_mod"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency", help="It adds the currency column on report if the currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries', default=True)
# MY ADD START
# В базу данных, в модель account.report.partner.ledger добавлено пользовательское поле x_partnrer_id типа many2one со ссылкой res.partner
# x_partner_id, x_accounts_id добавлено в метод _print_report в data
#MY ADD END
    x_partner_id = fields.Many2one('res.partner', string = 'Контрагент')
    x_accounts_id = fields.Many2many('account.account', string = 'Счета')
    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency, 'x_partner_id': self.x_partner_id.id, 'x_accounts_id': self.x_accounts_id.ids})
        return self.env['report'].get_action(self, 'account_extra_reports_rm.report_partnerledger_mod', data=data)
