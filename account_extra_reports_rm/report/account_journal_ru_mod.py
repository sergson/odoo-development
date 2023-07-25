# -*- coding: utf-8 -*-

import time
from openerp import api, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportJournalModified(models.AbstractModel):
    _name = 'report.account_extra_reports_rm.report_journal_mod'

    def lines(self, target_move, journal_ids, sort_selection, data):
        if isinstance(journal_ids, int):
            journal_ids = [journal_ids]

        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_ids)] + query_get_clause[2]
        query = 'SELECT "account_move_line".id FROM ' + query_get_clause[0] + ', account_move am, account_account acc WHERE "account_move_line".account_id = acc.id AND "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ORDER BY '
        if sort_selection == 'date':
            query += '"account_move_line".date'
        else:
            query += 'am.name'
        query += ', "account_move_line".move_id, acc.code'
        self.env.cr.execute(query, tuple(params))
        ids = map(lambda x: x[0], self.env.cr.fetchall())
        return self.env['account.move.line'].browse(ids)

    def _sum_debit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(debit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

# MY ADD START
    def _sum_debit_account(self, data, journal_id, acc_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        acc_id=str(acc_id)
        self.env.cr.execute('SELECT SUM(debit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND "account_move_line".account_id = '+acc_id+' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

# MY ADD END

# MY ADD START
    def _balance_account_before (self, data, journal_id, acc_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        data_before = data
        acc_id=str(acc_id)
#        data_before['form']['date_from'] = False
#        data_before['form']['date_to'] = (datetime.strptime(data['form']['date_from'],'%Y-%m-%d')- relativedelta(days=1)).strftime('%Y-%m-%d')
        query_get_clause = self._get_query_get_clause_before(data_before)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(debit - credit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND "account_move_line".account_id = '+acc_id+' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

# MY ADD END

# MY ADD START
    def _balance_account_full (self, data, journal_id, acc_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        data_full = data
        acc_id=str(acc_id)
        query_get_clause = self._get_query_get_clause_full(data_full)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(debit - credit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND "account_move_line".account_id = '+acc_id+' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

# MY ADD END




    def _sum_credit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(credit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

#MY ADD START

    def _sum_credit_account(self, data, journal_id, acc_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        acc_id=str(acc_id)
        self.env.cr.execute('SELECT SUM(credit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND "account_move_line".account_id = '+acc_id+' AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0
#MY ADD END

    def _get_taxes(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = """
            SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
            FROM account_move_line_account_tax_rel rel, """ + query_get_clause[0] + """ 
            LEFT JOIN account_move am ON "account_move_line".move_id = am.id
            WHERE "account_move_line".id = rel.account_move_line_id
                AND am.state IN %s
                AND "account_move_line".journal_id IN %s
                AND """ + query_get_clause[1] + """
           GROUP BY rel.account_tax_id"""
        self.env.cr.execute(query, tuple(params))
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]


        res = {}
        for tax in self.env['account.tax'].browse(ids):
            self.env.cr.execute('SELECT sum(debit - credit) FROM ' + query_get_clause[0] + ', account_move am '
                'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' AND tax_line_id = %s',
                tuple(params + [tax.id]))
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': self.env.cr.fetchone()[0] or 0.0,
            }
            if journal_id.type == 'sale':
                #sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res

    def _get_query_get_clause(self, data):
        return self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()

    def _get_query_get_clause_before(self, data):
        return self.env['account.move.line'].with_context(data['form'].get('used_context_before', {}))._query_get()

    def _get_query_get_clause_full(self, data):
        return self.env['account.move.line'].with_context(data['form'].get('used_context_full', {}))._query_get()



    @api.multi
    def render_html(self, data):
        target_move = data['form'].get('target_move', 'all')
        sort_selection = data['form'].get('sort_selection', 'date')

        res = {}
        for journal in data['form']['journal_ids']:
            res[journal] = self.with_context(data['form'].get('used_context', {})).lines(target_move, journal, sort_selection, data)
        docargs = {
            'doc_ids': data['form']['journal_ids'],
            'doc_model': self.env['account.journal'],
            'data': data,
            'docs': self.env['account.journal'].browse(data['form']['journal_ids']),
            'time': time,
            'lines': res,
            'sum_credit': self._sum_credit,
            'sum_debit': self._sum_debit,
            'sum_credit_account': self._sum_credit_account,
            'sum_debit_account': self._sum_debit_account,
            'get_taxes': self._get_taxes,
            'balance_account_before': self._balance_account_before,
            'balance_account_full': self._balance_account_full,
        }
        return self.env['report'].render('account_extra_reports_rm.report_journal_mod', docargs)
