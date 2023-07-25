# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp.addons.l10n_ru_doc.report_helper import QWebHelper

class report_stock_order(osv.AbstractModel):
    _name = 'report.stock_rm.report_stock_order'

    def render_html(self, cr, uid, ids, data=None, context=None):
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(cr, uid, 'stock_rm.report_stock_order')
        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': self.pool[report.model].browse(cr, uid, ids, context=context),
            'helper': QWebHelper(),
        }
        return report_obj.render(cr, uid, ids, 'stock_rm.report_stock_order', docargs, context=context)
