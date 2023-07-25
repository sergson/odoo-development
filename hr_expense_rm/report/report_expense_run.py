#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

#from openerp.addons.l10n_ru_doc.report_helper import QWebHelper
from openerp.addons.l10n_ru_doc.report_helper import QWebHelper
from openerp.osv import osv
from openerp.report import report_sxw
import logging
_logger = logging.getLogger(__name__)

class expense_run_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(expense_run_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_expense': self.get_expense,
            'helper': QWebHelper(),
            'get_account': self.get_account,
        })


    def get_expense(self, obj):
        expense_line = self.pool.get('hr.expense')
        res = []
        ids = []
        for e_id in range(len(obj)):
            ids.append(obj[e_id].id)
        if ids:
            res = expense_line.browse(self.cr, self.uid, ids)
#        _logger.debug('get_payslip:' + str(res))
        return res

    def get_account(self, obj):
        move_line = self.pool.get('account.move.line')
        accounts = []
        res = []
        if obj.account_move_id:
            expense_move_id = obj.account_move_id.id
            if expense_move_id:
                move_lines_ids = move_line.search(self.cr, self.uid, [('move_id', '=', expense_move_id)])
                move_lines = move_line.browse(self.cr, self.uid, move_lines_ids)
                for line in move_lines:
                     if line.debit > 0:
                         accounts.append(line.account_id.code)
#        _logger.debug('get_payslip:' + str(res))
        res = ', '.join(accounts) 
        return res


class wrapped_report_expense_run(osv.AbstractModel):
    _name = 'report.hr_expense_rm.report_expense_run'
    _inherit = 'report.abstract_report'
    _template = 'hr_expense_rm.report_expense_run'
    _wrapped_report_class = expense_run_report
