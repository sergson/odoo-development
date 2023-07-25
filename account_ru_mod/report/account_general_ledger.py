# -*- coding: utf-8 -*-

import time
from openerp import api, models, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)



class ReportGeneralLedgerModified(models.AbstractModel):
    _name = 'report.account_ru_mod.report_generalledger_modified'

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
#MY ADD START
            date_from_before = str(self.env.context.get('date_from'))
            _logger.debug('DATE_FROM_BEFORE: '+ date_from_before)
            date_to_before = (datetime.strptime(date_from_before,'%Y-%m-%d')- relativedelta(days=1)).strftime('%Y-%m-%d')
#MY ADD END

#            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_to=self.env.context.get('date_from'), date_from=False)._query_get()
# DOWN LINE MODIFED BY ME
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_to=date_to_before,
                                                                                      date_from=False)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                                        '' AS move_name, '' AS move_id, '' AS currency_code,\
                                        NULL AS currency_id,\
                                        '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                                        '' AS partner_name, '' AS acccode\
                                        FROM account_move_line l\
                                        LEFT JOIN account_move m ON (l.move_id=m.id)\
                                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                                        LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                                        JOIN account_journal j ON (l.journal_id=j.id)\
                                        JOIN account_account acc ON (l.account_id = acc.id)\
                                        WHERE l.account_id IN %s" + filters + ' GROUP BY l.account_id ')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.name, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.name AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                            m.name AS move_name, m.id AS move_id, c.symbol AS currency_code, p.name AS partner_name, acc.code AS acccode\
                            FROM account_move_line l\
                            JOIN account_move m ON (l.move_id=m.id)\
                            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                            JOIN account_journal j ON (l.journal_id=j.id)\
                            JOIN account_account acc ON (l.account_id = acc.id)\
                            WHERE l.account_id IN %s ' + filters + ' GROUP BY l.id, l.account_id, l.date, j.name, l.currency_id, l.amount_currency, l.ref, l.name, m.name, m.id, c.symbol, p.name, acc.code ORDER BY ' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            # my add start
            for line in move_lines[account.id]:
                if 'move_id' not in line:
                    continue
                line_move_id = line['move_id']
                line_acc_id = account.id
                line_debit = line['debit']
                line_credit = line['credit']
                wheres = [""]
                if line_move_id:
                    wheres.append('l.move_id = ' + str(line_move_id))
                    if line_acc_id or line_credit:
                        wheres.append('AND')
                if line_acc_id:
                    wheres.append('l.account_id != ' + str(line_acc_id))
                    if line_credit:
                        wheres.append('AND')
                if line_credit:
                    wheres.append('(l.debit = ' + str(line_credit) + ' AND l.credit = ' + str(line_debit) + ')')
                filters = " ".join(wheres)
                #                sql = ('SELECT acc.code AS acccode\
                #                    FROM account_move_line l\
                #                    JOIN account_account acc ON (l.account_id = acc.id)\
                #                    WHERE l.move_id = '+ str(line_move_id) + ' AND l.account_id != ' + str(line_acc_id) + ' AND\
                #                    (l.debit = ' + str(line_credit) + ' AND l.credit = ' + str(line_debit) + ')')
                sql = ('SELECT acc.code AS acccode\
                                    FROM account_move_line l\
                                    JOIN account_account acc ON (l.account_id = acc.id)\
                                    WHERE ' + filters + ' ')
                cr.execute(sql)
                #                _logger.debug('sql ' + str(cr.fetchall()))
                #                _logger.debug('sql ' + str(sql))
                line_acc_code = ''
                for row in cr.dictfetchall():
                    code = row['acccode']
                    if code not in line_acc_code:
                        line_acc_code += (str(code) + ' ')
                line['acccode'] = line_acc_code
# my add end
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.name for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
 
#MY ADD START       
        x_account_id = data['form']['x_account_id']
        if x_account_id:
            accounts = self.env['account.account'].browse(x_account_id)
        else:
            accounts = self.env['account.account'].search([])            

#        lines_of_move_ids = self.env['account.move.line'].search(['id', '=', 118])

#MY ADD END
        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }
        return self.env['report'].render('account_ru_mod.report_generalledger_modified', docargs)
