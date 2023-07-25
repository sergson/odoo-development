# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountTaxInherited(models.Model):
    _inherit = 'account.tax'

    x_corr_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Корреспондирующий счет', ondelete='restrict', help="Если выбран, то для учета сумм налога в хозяйственной операции, вместо счета для расчетов с контрагентом, используется этот счет.")