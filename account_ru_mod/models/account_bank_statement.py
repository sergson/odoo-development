# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError

class AccountBankStatementInherited(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def unlink(self):
#MY ADD START
        all_users=self.pool.get('res.users')
        cr=self._cr
        uid=self._uid
        if all_users.has_group(cr, uid, 'account.group_account_manager'):
            return super(AccountBankStatementInherited, self).unlink()
        else:
#MY ADD END
            for statement in self:
                if statement.state != 'open':
                    raise UserError(_('In order to delete a bank statement, you must first cancel it to delete related journal items.'))
            # Explicitly unlink bank statement lines so it will check that the related journal entries have been deleted first
            statement.line_ids.unlink()
            return super(AccountBankStatementInherited, self).unlink()


class AccountBankStatementLineName(models.Model):
    _name = "account.bank.statement.line.name"
    _description = "Bank Statement Line Name"

    name = fields.Char(string='Основание', required=True)


class AccountBankStatementLineInherited(models.Model):
    _inherit = 'account.bank.statement.line'

    base = fields.Many2one('account.bank.statement.line.name', string='Основание')

    @api.multi
    def unlink(self):
#MY ADD START
        all_users=self.pool.get('res.users')
        cr=self._cr
        uid=self._uid
        if all_users.has_group(cr, uid, 'account.group_account_manager'):
            return super(AccountBankStatementLineInherited, self).unlink()
        else:
#MY ADD END
            for line in self:
                if line.journal_entry_ids.ids:
                    raise UserError(_('In order to delete a bank statement line, you must first cancel it to delete related journal items.'))
            return super(AccountBankStatementLineInherited, self).unlink()