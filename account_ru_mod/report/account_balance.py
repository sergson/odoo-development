# -*- coding: utf-8 -*-

import time
from openerp import api, models
#ADD BY ME START
import logging
_logger = logging.getLogger(__name__)
#ADD BY ME END

class ReportTrialBalanceModified(models.AbstractModel):
    _name = 'report.account_ru_mod.report_trialbalance_modified'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
#            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
#MOD BY ME
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'balance_before', 'balance_full'])
#MOD BY ME
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res


    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
#        docs = self.env[self.model].browse(self.env.context.get('active_id')) #old v
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
#        accounts = self.env['account.account'].search([])
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
#        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
#ADD BY ME START
        account_res = []
        accounts_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, 'all')
        accounts_res_before = self.with_context(data['form'].get('used_context_before'))._get_accounts(accounts, 'all')
        accounts_res_full = self.with_context(data['form'].get('used_context_full'))._get_accounts(accounts, 'all')
        for i, account in enumerate(accounts_res):
            for account_before in accounts_res_before:
                if account_before['code'] == account['code']:
                    account.update({'balance_before': account_before['balance']})
                    accounts_res[i] = account
                    break
            for account_full in accounts_res_full:
                if account_full['code'] == account['code']:
                    account.update({'balance_full': account_full['balance']})
                    accounts_res[i] = account
                    break
            if display_account in ['movement'] and any([account['debit'], account['credit']]):
                account_res.append(accounts_res[i])
            elif display_account in ['not_zero'] and abs(account['balance_full']) >= 0.01:
                account_res.append(accounts_res[i])
            elif display_account in ['all'] and any(
                    [account['balance'], account['balance_full'], account['balance_before'], account['debit'],
                     account['credit']]):
                account_res.append(accounts_res[i])
#        _logger.debug ('ACCOUTS_RES: '+str(account_res))      
#ADD BY ME END
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
        return self.env['report'].render('account_ru_mod.report_trialbalance_modified', docargs)
