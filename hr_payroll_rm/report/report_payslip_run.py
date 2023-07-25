#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.addons.l10n_ru_doc.report_helper import QWebHelper
from openerp.osv import osv
from openerp.report import report_sxw
import logging
_logger = logging.getLogger(__name__)

class payslip_run_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(payslip_run_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_worked_days': self.get_payslip_worked_days,
            'get_payslip_run_lines': self.get_payslip_run_lines,
            'get_payslip': self.get_payslip,
            'get_payslip_run_line_by_code': self.get_payslip_run_line_by_code,
            'get_payslip_run_total_by_code': self.get_payslip_run_total_by_code,
            'helper': QWebHelper(),
        })


    def get_payslip_worked_days(self, obj):
        payslip_line = self.pool.get('hr.payslip.worked_days')
        res = []
        ids = []
        for s_id in range(len(obj)):
            for w_id in range(len(obj[s_id].worked_days_line_ids)):
                    ids.append(obj[s_id].worked_days_line_ids[w_id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        _logger.debug(' get_payslip_worked_days:' + str(res))
        return res

    def get_payslip_run_lines(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for s_id in range(len(obj)):
            for l_id in range(len(obj[s_id].line_ids)):
                if obj[s_id].line_ids[l_id].appears_on_payslip is True:
                    ids.append(obj[s_id].line_ids[l_id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        _logger.debug('get_payslip_run_lines:' + str(res))
        return res
    
    def get_payslip_run_line_by_code(self, obj, context):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for s_id in range(len(obj)):
            for l_id in range(len(obj[s_id].line_ids)):
                if (obj[s_id].line_ids[l_id].appears_on_payslip is True) and (obj[s_id].line_ids[l_id].code == context):
                    ids.append(obj[s_id].line_ids[l_id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        _logger.debug('get_payslip_run_line_by_code:' + str(res))
        return res

    def get_payslip_run_total_by_code(self, obj, context):
        payslip_line = self.pool.get('hr.payslip.line')
        res = 0
        ids = []
        res_ids=[]
        for s_id in range(len(obj)):
            for l_id in range(len(obj[s_id].line_ids)):
                if (obj[s_id].line_ids[l_id].appears_on_payslip is True) and (obj[s_id].line_ids[l_id].code == context):
                    ids.append(obj[s_id].line_ids[l_id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)[0].total
#            for line in res_ids:
#                res.append(line.total)
#        _logger.debug(' get_payslip_run_total_by_code:' + str(res))
        return res


    def get_payslip(self, obj):
        payslip_line = self.pool.get('hr.payslip')
        res = []
        ids = []
        for s_id in range(len(obj)):
            ids.append(obj[s_id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        _logger.debug('get_payslip:' + str(res))
        return res


class wrapped_report_payslip_run(osv.AbstractModel):
    _name = 'report.hr_payroll_rm.report_payslip_run'
    _inherit = 'report.abstract_report'
    _template = 'hr_payroll_rm.report_payslip_run'
    _wrapped_report_class = payslip_run_report
