# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
from openerp import api, fields, models
_logger = logging.getLogger(__name__)


class ReportOverdueModified(models.AbstractModel):
    _inherit = 'report.account.report_overdue'

    def _get_account_move_lines(self, partner_ids):
        res = dict(map(lambda x: (x, []), partner_ids))
        self.env.cr.execute(
            "SELECT m.name AS move_id, l.date, l.name, l.ref, l.date_maturity, l.partner_id, l.blocked, l.amount_currency, l.currency_id, "
            "CASE WHEN at.type IN ('receivable', 'payable')"
            "THEN SUM(l.debit) "
            "ELSE SUM(l.credit * 0) "
            "END AS debit, "
            "CASE WHEN at.type IN ('receivable', 'payable')"
            "THEN SUM(l.credit) "
            "ELSE SUM(l.debit * 0) "
            "END AS credit, "
            "CASE WHEN l.date_maturity < %s "
            "THEN SUM(l.debit - l.credit) "
            "ELSE 0 "
            "END AS mat "
            "FROM account_move_line l "
            "JOIN account_account_type at ON (l.user_type_id = at.id) "
            "JOIN account_move m ON (l.move_id = m.id) "
            "WHERE l.partner_id IN %s AND at.type IN ('receivable', 'payable') GROUP BY l.date, l.name, l.ref, l.date_maturity, l.partner_id, at.type, l.blocked, l.amount_currency, l.currency_id, l.move_id, m.name ORDER BY l.date DESC",
            (((fields.date.today(),) + (tuple(partner_ids),))))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    @api.multi
    def render_html(self, data):
        totals = {}
        lines = self._get_account_move_lines(self.ids)
        lines_to_display = {}
        company_currency = self.env.user.company_id.currency_id
        start_date = False #MY var
        for partner_id in self.ids:
            lines_to_display[partner_id] = {}
            totals[partner_id] = {}
            for line_tmp in reversed(lines[partner_id]):
                line = line_tmp.copy()
                currency = line['currency_id'] and self.env['res.currency'].browse(line['currency_id']) or company_currency
                if currency not in lines_to_display[partner_id]:
                    lines_to_display[partner_id][currency] = []
                    totals[partner_id][currency] = dict((fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
                if line['debit'] and line['currency_id']:
                    line['debit'] = line['amount_currency']
                if line['credit'] and line['currency_id']:
                    line['credit'] = line['amount_currency']
                if line['mat'] and line['currency_id']:
                    line['mat'] = line['amount_currency']
                lines_to_display[partner_id][currency].append(line)
                if not line['blocked']:
                    totals[partner_id][currency]['due'] += line['debit']
                    totals[partner_id][currency]['paid'] += line['credit']
                    totals[partner_id][currency]['mat'] += line['mat']
                    totals[partner_id][currency]['total'] += line['debit'] - line['credit']
#MY ADD Start
                if not start_date:
                    start_date=line['date']
                else:
                    if line['date']<start_date:
                        start_date=line['date']
#MY ADD END
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(self.ids),
            'time': time,
            'Lines': lines_to_display,
            'Totals': totals,
#            'Date': str(fields.date.today())
            'Date': datetime.strptime(str(fields.date.today()),'%Y-%m-%d').strftime('%d.%m.%Y'),
            'Start_date': datetime.strptime(str(start_date),'%Y-%m-%d').strftime('%d.%m.%Y')
        }
        _logger.debug(str(docargs))
        return self.env['report'].render('account_ru_mod.report_overdue_document_modified', values=docargs)
