# -*- coding: utf-8 -*-

import time
from openerp import api, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ReportAgedPartnerBalanceModified(models.AbstractModel):

    _name = 'report.account_ru_mod.report_agedpartnerbalance_modified'

    def _get_account_move_entry(self, accounts, init_balance, x_sortby, x_display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                x_display_account: type of account(receivable, payable and both)

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
#            _logger.debug('DATE_FROM_BEFORE: '+ date_from_before)
            date_to_before = (datetime.strptime(date_from_before,'%Y-%m-%d')- relativedelta(days=1)).strftime('%Y-%m-%d')
#MY ADD END

#            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_to=self.env.context.get('date_from'), date_from=False)._query_get()
# DOWN LINE MODIFED BY ME
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_to=date_to_before, date_from=False)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
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
        if x_sortby == 'sort_journal_partner':
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
                sql = ('SELECT acc.code AS acccode\
                    FROM account_move_line l\
                    JOIN account_account acc ON (l.account_id = acc.id)\
                    WHERE l.move_id = '+ str(line_move_id)+ ' AND l.account_id != ' + str(line_acc_id) + ' AND\
                    (l.debit = ' + str(line_credit) + ' AND l.credit = ' + str(line_debit)+')')
                cr.execute(sql)
#                _logger.debug('sql ' + str(cr.fetchall()))
#                _logger.debug('sql ' + str(sql))
                line_acc_code = ''
                for row in cr.dictfetchall():
                  code=row['acccode']
                  line_acc_code += (str(code) + ' ')
                line['acccode'] = line_acc_code
# my add end

            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                if line['lname']!='Initial Balance':
                    res['debit'] += line['debit']
                    res['credit'] += line['credit']
                res['balance'] = line['balance']
            if x_display_account == 'all':
                account_res.append(res)
            if x_display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if x_display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res

# MY ADD START
    def _accounts_rev (self, accounts_res): 
        account_rev_res = []
#        _logger.debug('rev'+str(accounts_res))
#        return account_rev_res
        if accounts_res:
            for account in accounts_res:
                res={}
                res['code']=account['code']
                res['name']=account['name']
                res['move_lines']=account['move_lines']
                res['debit']=account['debit']
                res['credit']=account['credit']
                res['balance']=account['balance']
                acc_codes=[]
                for line in account.get('move_lines'):
#                    _logger.debug('line'+str(line))
                    if acc_codes:
                        for acc_code in acc_codes:
                            if line['acccode'] not in acc_codes:
                                acc_codes.append(line['acccode'])
                    else:
                        acc_codes.append(line['acccode'])
                if acc_codes:
                    res['corracc']=[]
                    for acc_code in acc_codes:
                        res_coracc = dict((fn, 0.0) for fn in ['credit', 'debit'])
                        for line in account.get('move_lines'): 
                            if acc_code == line['acccode']:
                                res_coracc['corracccode'] = acc_code
                                res_coracc['debit'] += line['debit']
                                res_coracc['credit'] += line['credit']
                        res['corracc'].append(res_coracc)
                    account_rev_res.append(res)
#                _logger.debug('acccodes'+str(acc_codes))
        _logger.debug('rev'+str(account_rev_res))
        return account_rev_res
# MY ADD END

    def _get_partner_move_lines(self, form, account_type, date_from, target_move):
        res = []
        self.total_account = []
        cr = self.env.cr
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id = account_account.id) \
                    AND (l.move_id = am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.internal_type IN %s)\
                    AND l.reconciled IS FALSE\
                    AND (l.partner_id = res_partner.id)\
                    AND (l.date <= %s)\
                ORDER BY res_partner.name', (tuple(move_state), tuple(account_type), date_from))

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            self.total_account.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['id'] for partner in partners]
        if not partner_ids:
            return []

        # This dictionary will store the debit-credit for all partners, using partner_id as key.
        totals = {}
        cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.internal_type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(account_type), tuple(partner_ids), date_from,))
        partner_totals = cr.fetchall()
        for partner_id, amount in partner_totals:
            totals[partner_id] = amount
        # This dictionary will store the future or past of all partners
        future_past = {}
        cr.execute('SELECT l.partner_id, SUM(l.debit - l.credit) \
                FROM account_move_line AS l, account_account, account_move am \
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)\
                    AND (am.state IN %s)\
                    AND (account_account.internal_type IN %s)\
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND (l.partner_id IN %s)\
                    AND l.reconciled IS FALSE\
                AND (l.date <= %s)\
                    GROUP BY l.partner_id', (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from,))
        partner_totals = cr.fetchall()
        for partner_id, amount in partner_totals:
            future_past[partner_id] = amount
        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (date_from,)
            cr.execute('''SELECT l.partner_id, SUM(l.debit - l.credit), l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (l.partner_id IN %s)
                        AND l.reconciled IS FALSE
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id, l.id''', args_list)
            partners_partial = cr.fetchall()
            partners_amount = dict((partner_id, 0) for partner_id, amount, line_id in partners_partial)
            for partner_id, amount, line_id in partners_partial:
                partial_reconcile_ids = []
                line = self.env['account.move.line'].browse(line_id)
                for partial_line in (line.matched_debit_ids + line.matched_credit_ids):
                    if not partial_line.credit_move_id.id in partial_reconcile_ids:
                        partial_reconcile_ids.append(partial_line.credit_move_id.id)
                    if not partial_line.debit_move_id.id in partial_reconcile_ids:
                        partial_reconcile_ids.append(partial_line.debit_move_id.id)
                if partial_reconcile_ids:
                   # in case of partial reconciliation, we want to keep the left amount in the oldest period
                    cr.execute('''SELECT MIN(COALESCE(date_maturity, date)) from account_move_line where id = %s''', (line_id,))
                    date = cr.fetchall()
                    partial = False
                    if 'BETWEEN' in dates_query:
                        partial = date and args_list[-3] <= date[0][0] <= args_list[-2]
                    elif '>=' in dates_query:
                        partial = date and date[0][0] >= form[str(i)]['start']
                    else:
                        partial = date and date[0][0] <= form[str(i)]['stop']
                    if partial:
                       # partial reconcilation
                        limit_date = 'COALESCE(l.date_maturity, l.date) <= %s'
                        cr.execute('''SELECT SUM(l.debit - l.credit)
                                           FROM account_move_line AS l, account_move AS am
                                           WHERE l.move_id = am.id AND am.state IN %s
                                           AND l.id IN %s
                                           AND ''' + limit_date, (tuple(move_state), tuple(partial_reconcile_ids), date_from))
                        unreconciled_amount = cr.fetchall()
                        partners_amount[partner_id] += unreconciled_amount[0][0]
                else:
                    partners_amount[partner_id] += amount
            history.append(partners_amount)
        for partner in partners:
            values = {}
            # Query here is replaced by one query which gets the all the partners their 'after' value
            after = False
            if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                after = [ future_past[partner['id']] ]
            self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
            values['direction'] = after and after[0] or 0.0
            for i in range(5):
                during = False
                if history[i].has_key(partner['id']):
                    during = [ history[i][partner['id']] ]
               # Adding counter
                self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key( partner['id'] ):
                total = [ totals[partner['id']] ]
            values['total'] = total and total[0] or 0.0
           ## Add for total
            self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            res.append(values)
        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res
    def _get_move_lines_with_out_partner(self, form, account_type, date_from, target_move):
        res = []
        cr = self.env.cr
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        ## put a total of 0
        for i in range(7):
            self.total_account.append(0)
        totals = {}
        cr.execute('SELECT SUM(l.debit - l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)\
                    AND (am.state IN %s)\
                    AND (l.partner_id IS NULL)\
                    AND (account_account.internal_type IN %s)\
                    AND l.reconciled IS FALSE \
                    AND (l.date <= %s)\
                    ',(tuple(move_state), tuple(account_type), date_from,))
        total_amount = cr.fetchall()
        for amount in total_amount:
            totals['Unknown Partner'] = amount[0]
        future_past = {}
        cr.execute('SELECT SUM(l.debit-l.credit) \
                FROM account_move_line AS l, account_account, account_move am \
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)\
                    AND (am.state IN %s)\
                    AND (l.partner_id IS NULL)\
                    AND (account_account.internal_type IN %s)\
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND l.reconciled IS FALSE\
                    ', (tuple(move_state), tuple(account_type), date_from,))
        total_amount = cr.fetchall()
        for amount in total_amount:
            future_past['Unknown Partner'] = amount[0]

        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type))
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (date_from,)
            cr.execute('SELECT SUM(l.debit - l.credit)\
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.internal_type IN %s)\
                        AND (l.partner_id IS NULL)\
                        AND l.reconciled IS FALSE\
                        AND ' + dates_query + '\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id', args_list)
            total_amount = cr.fetchall()
            history_data = {}
            for amount in total_amount:
                history_data['Unknown Partner'] = amount[0]
            history.append(history_data)
        values = {}
        after = False
        if future_past.has_key('Unknown Partner'):
            after = [ future_past['Unknown Partner'] ]
        self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
        values['direction'] = after and after[0] or 0.0
        for i in range(5):
            during = False
            if history[i].has_key('Unknown Partner'):
                during = [ history[i]['Unknown Partner'] ]
            self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
            values[str(i)] = during and during[0] or 0.0
        total = False
        if totals.has_key( 'Unknown Partner' ):
            total = [ totals['Unknown Partner'] ]
        values['total'] = total and total[0] or 0.0
       ## Add for total
        self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
        values['name'] = 'Unknown Partner'
        if values['total']:
            res.append(values)
        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res

    @api.multi
    def render_html(self, data):
        self.total_account = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        x_init_balance = data['form'].get('x_initial_balance', True)
        x_sortby = data['form'].get('x_sortby', 'sort_date')
        x_display_account = data['form']['x_display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.name for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

#MY ADD START
        account_id = data['form']['x_account_id']
        if account_id:
            accounts = self.env['account.account'].browse(account_id)
        else:
            accounts = self.env['account.account'].search([])

#MY ADD END
        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, x_init_balance, x_sortby, x_display_account)
        accounts_rev=self._accounts_rev(accounts_res)

#        target_move = data['form'].get('target_move', 'all')
#        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
#        if data['form']['result_selection'] == 'customer':
#            account_type = ['receivable']
#        elif data['form']['result_selection'] == 'supplier':
#            account_type = ['payable']
#        else:
#            account_type = ['payable','receivable']
#        without_partner_movelines = self._get_move_lines_with_out_partner(data['form'], account_type, date_from, target_move)
#        partner_movelines = self._get_partner_move_lines(data['form'], account_type, date_from, target_move)
#        movelines = partner_movelines + without_partner_movelines
#        docargs = {
#            'doc_ids': self.ids,
#            'doc_model': model,
#            'data': data['form'],
#            'docs': docs,
#            'time': time,
#            'get_partner_lines': movelines,
#            'get_direction': self.total_account,
#            'Accounts': accounts_res,
#            'print_journal': codes,
#         }
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
            'accounts_rev': accounts_rev,
        }
        return self.env['report'].render('account_ru_mod.report_agedpartnerbalance_modified', docargs)