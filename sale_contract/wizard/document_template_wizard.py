# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _


class template_wizard(models.TransientModel):
    _name = "sale.contract.doc.templ.wizard"
    _description = 'Wizard to select documents by contract from templates'

    document_template_ids = fields.Many2many('sale.contract.doc.templ', string = 'Document template', required = True, help = "Select document templates")
    
    @api.multi
    def  documents_return(self, context=None):
        sale_order_id = context.get('sale_order_id')
        for document_template in self.document_template_ids:
            vals = {
                'name' : document_template.name,
                'sale_order_id': sale_order_id,
                'state' : 'draft'
            }
            document = self.env['sale.contract.doc'].create(vals)
            for templ_cond in document_template.terms:
                vals_cond = {
                    'cond_model':templ_cond.cond_model,
                    'condition_python':templ_cond.condition_python,
                    'ext_vals':templ_cond.ext_vals, 
                    'false_replace':templ_cond.false_replace,
                    'name':templ_cond.name,
                    'term_text':templ_cond.term_text,
                    'sale_contract_doc_id':document.id,
                    'sequence':templ_cond.sequence,
                } 
                doc_cond= self.env['sale.cont.doc.cond'].create(vals_cond)
        return True
