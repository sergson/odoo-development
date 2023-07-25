# -*- coding: utf-8 -*-

import time
from openerp import api, models
import logging
_logger = logging.getLogger(__name__)


class ReportFinancialInherited(models.AbstractModel):
    _inherit = 'report.account.report_financial'

    def _compute_account_balance(self, accounts, corr_acc_ids = False, corr_acc_logic = False):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
#MY ADD
            if corr_acc_ids:
                ids_line = tuple(corr_acc_ids.ids)
                _logger.debug('ids_line: ' + str(ids_line))
                corr_acc_line_ids = self.env['account.move.line'].search([('account_id', 'in', ids_line)])
                if corr_acc_line_ids:
                    corr_acc_move_ids = []
                    for corr_acc_line in corr_acc_line_ids:
                        corr_acc_move_ids.append(corr_acc_line.move_id.id)
                    ids_move = tuple(corr_acc_move_ids)
                    _logger.debug('move_ids: ' + str(corr_acc_move_ids))
                    if corr_acc_logic == 1:
                        filters_acc_ids = "(account_id in %s AND (\"account_move_line__move_id\".\"id\" in " + str(
                            ids_move) + "))"
                    elif corr_acc_logic == -1:
                        filters_acc_ids = "(account_id in %s AND (\"account_move_line__move_id\".\"id\" not in " + str(
                            ids_move) + "))"
                    else:
                        filters_acc_ids = "account_id IN %s"
                else:
                    filters_acc_ids = "account_id IN %s"
            else:
                filters_acc_ids = "account_id IN %s"
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                      " FROM " + tables + \
                      " WHERE " + \
                      filters_acc_ids + \
                      filters + \
                      " GROUP BY account_id"
#MY MOD END
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        fields_rev = ['credit', 'debit']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids, report.x_corr_acc, report.x_corr_acc_formula)
                for value in res[report.id]['account'].values():
                    for field in fields_rev:
                        res[report.id][field] += value.get(field)
#MY ADD Start
                    if not report.x_rev_type or report.x_rev_type == 0:
                        if value.get('balance') > 0 and report.x_balance_formula > 0 or value.get(
                                'balance') < 0 and report.x_balance_formula < 0 or report.x_balance_formula == 0 or not report.x_balance_formula:
                            res[report.id]['balance'] += value.get('balance')
                    elif report.x_rev_type == 1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('debit')
                    elif report.x_rev_type == -1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('credit')
#MY ADD End
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(accounts)
                for value in res[report.id]['account'].values():
                    for field in fields_rev:
                        res[report.id][field] += value.get(field)
#MY ADD Start
                    if not report.x_rev_type or report.x_rev_type == 0:
                        if value.get('balance') > 0 and report.x_balance_formula > 0 or value.get(
                                'balance') < 0 and report.x_balance_formula < 0 or report.x_balance_formula == 0 or not report.x_balance_formula:
                            res[report.id]['balance'] += value.get('balance')
                    elif report.x_rev_type == 1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('debit')
                    elif report.x_rev_type == -1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('credit')
#MY ADD End
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id)
                for key, value in res2.items():
                    for field in fields_rev:
                        res[report.id][field] += value[field]
#MY ADD Start
                    if not report.x_rev_type or report.x_rev_type == 0:
                        if value.get('balance') > 0 and report.x_balance_formula > 0 or value.get(
                                'balance') < 0 and report.x_balance_formula < 0 or report.x_balance_formula == 0 or not report.x_balance_formula:
                            res[report.id]['balance'] += value.get('balance')
                    elif report.x_rev_type == 1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('debit')
                    elif report.x_rev_type == -1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('credit')

#MY ADD End
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids)
                for key, value in res2.items():
                    for field in fields_rev:
                        res[report.id][field] += value[field]
#MY ADD Start
                    if not report.x_rev_type or report.x_rev_type == 0:
                        if value.get('balance') > 0 and report.x_balance_formula > 0 or value.get(
                                'balance') < 0 and report.x_balance_formula < 0 or report.x_balance_formula == 0 or not report.x_balance_formula:
                            res[report.id]['balance'] += value.get('balance')
                    elif report.x_rev_type == 1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('debit')
                    elif report.x_rev_type == -1 and (not report.x_corr_acc_formula or not report.x_corr_acc):
                        res[report.id]['balance'] += value.get('credit')

#MY ADD End
        return res


    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()

# MY ADD START
        child_reports = sorted(child_reports, key=lambda line: line.sequence)
# MY ADD END
 
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

            lines.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines