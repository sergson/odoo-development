# -*- coding: utf-8 -*-

import time
import logging
_logger = logging.getLogger(__name__)

from openerp import api, models


class ReportSaleContractDoc(models.AbstractModel):
    _name = 'report.sale.contract.doc'


    @api.multi
    def render_html(self, data = None):

        report = self.env['report']
        docs = self.env[report.model].browse(self.env.context.get('active_id'))

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
        }

        return report.render('sale_contract.sale_contract_doc_report', docargs)
