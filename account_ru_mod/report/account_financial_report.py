# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, models, fields

# ---------------------------------------------------------
# Account Financial Report
# ---------------------------------------------------------


class accountFinancialReportInherited(models.Model):
    _inherit = "account.financial.report"

    x_balance_formula = fields.Selection([(0, 'все'), (1, 'только дебит'), (-1, 'только кредит')], 'Остаток баланса', required=False, default=0)
    x_rev_type = fields.Selection([(0, 'все'), (1, 'только дебет'), (-1, 'только кредит')], 'Вид оборота', required=False, default=0)
    x_corr_acc = fields.Many2many('account.account', 'account_account_financial_report_rel', 'account_financial_report_id', 'account_account_id', 'Корр. счета')
    x_corr_acc_formula = fields.Selection([(1, 'учитывать оборот только с выбранных'), (-1, 'исключать оборот с выбранных')], 'Расчет оборотов с корр. счетов', required=False, default=0)
