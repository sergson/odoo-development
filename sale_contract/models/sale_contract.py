# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval
import re
import math
from pytils import numeral,dt
import logging
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _

class sale_contract_doc_templ(models.Model):
    _name = "sale.contract.doc.templ"
    _description = 'Templates of documents'
    _order = "name"

    name = fields.Char('Document template name', help="Name of document template", required=True)
    terms = fields.One2many('sale.cont.doc.templ.cond', 'sale_contract_doc_templ_id', string = 'Document template terms', help="Conditions in  Qweb format for document temlate")

class sale_cont_doc_templ_cond(models.Model):
    _name = "sale.cont.doc.templ.cond"
    _description = 'Document template conditions'
    _order = "sequence"

    cond_model = fields.Selection([
        ('sale.order', 'Sale order'),
        ('sale.order.line', 'Sale order line'),
        ], string='Condition model', default='sale.order')
    condition_python = fields.Text('Python code', help='Python code for example: result = [company.name, model.name, 2+2, {field name, no cyrillic}, datetime.strptime(model.date_order, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")] for insert result in qweb use: {result[0]} {result[1]} ... in term field')
    false_replace = fields.Boolean(string='Remove False in Qweb text', help="This option remove False that included in Qweb text from without values fields", default = True)
    ext_vals = fields.Text('Condition external values', help="Comma with space separated field names of selected model for including in conditions, though {name1.model_field},{name2}...")
    name = fields.Char('Conditin short name', help = "Short for explain of condition")
    term_text = fields.Text('Qweb text', help="Qweb (html) formated text for report. Insetr a {field name from condition external value with trought point separated item name} or {result} to add model values to qweb")
    sale_contract_doc_templ_id = fields.Many2one('sale.contract.doc.templ', string = 'Related document template')
    sequence = fields.Integer('Sequence') 

class sale_contract_doc(models.Model):
    _name = "sale.contract.doc"
    _description = 'Documents for sale order'
    _order = "name"

    name = fields.Char('Document name', help="Name of document or sale contarct", required=True)
    sale_order_id = fields.Many2one('sale.order', string = 'Sale order')
    state =  fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Offer'),
        ('done', 'Acceptance'),
        ('cancel', 'Dissolved'),
        ], string = 'Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    terms = fields.One2many('sale.cont.doc.cond', 'sale_contract_doc_id', string = 'Document terms', readonly=True, states={'draft': [('readonly', False)]}, help="Conditions, Qweb format for document")

    @api.multi
    def print_doc(self):
        return self.env['report'].get_action(self, 'sale_contract.sale_contract_doc_report')

    @api.multi
    def doc_to_template(self, context=None):
        vals = {
            'name' : self.name
        }
        document = self.env['sale.contract.doc.templ'].create(vals)
        for cond in self.terms:
            vals_cond = {
                'cond_model':cond.cond_model,
                'condition_python':cond.condition_python,
                'ext_vals':cond.ext_vals, 
                'false_replace':cond.false_replace,
                'name':cond.name,
                'term_text':cond.term_text,
                'sale_contract_doc_templ_id':document.id,
                'sequence':cond.sequence,
            } 
            doc_cond= self.env['sale.cont.doc.templ.cond'].create(vals_cond)
        return True

    @api.multi
    def sent_doc(self):
        docs = self.filtered(lambda s: s.state in ['draft'])
        docs.write({
            'state': 'sent'
        })

    @api.multi
    def done_doc(self):
        docs = self.filtered(lambda s: s.state in ['sent'])
        docs.write({
            'state': 'done'
        })

    @api.multi
    def cancel_doc(self):
        docs = self.filtered(lambda s: s.state in ['draft', 'sent', 'done'])
        docs.write({
            'state': 'cancel'
        })

    @api.multi
    def draft_doc(self):
        docs = self.filtered(lambda s: s.state in ['sent', 'cancel'])
        docs.write({
            'state': 'draft'
        })


class sale_cont_doc_cond(models.Model):
    _name = "sale.cont.doc.cond"
    _description = 'Document conditions'
    _order = "sequence"

    cond_model = fields.Selection([
        ('sale.order', 'Sale order'),
        ('sale.order.line', 'Sale order line'),
        ], string='Condition model', default='sale.order')
    condition_python = fields.Text('Python code', help='Python code for example: result = [company.name, model.name, 2+2, {field name, no cyrillic}, datetime.strptime(model.date_order, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")] for insert result in qweb use: {result[0]} {result[1]} ... in term field')
    false_replace = fields.Boolean(string='Remove False in Qweb text', help="This option remove False that included in Qweb text from without values fields", default = True)
    ext_vals = fields.Text('Condition external values', help="Comma with space separated field names of selected model for including in conditions, though {name1.model_field},{name2}...")
    name = fields.Char('Conditin short name', help = "Short for explain of condition")
    term_text = fields.Text('Qweb text', help="Qweb (html) formated text for report. Insetr a {field name from condition external value with trought point separated item name} or {result} to add model values to qweb")
    report_text = fields.Html('Report view', compute = '_compute_report_line', help="View of condition on report")
    sale_contract_doc_id = fields.Many2one('sale.contract.doc', string = 'Related document')
    sale_order_id = fields.Many2one('sale.order', string = 'Sale order', related = 'sale_contract_doc_id.sale_order_id')
    sequence = fields.Integer('Sequence') 

    @api.depends('term_text', 'ext_vals', 'condition_python')
    def _compute_report_line(self):
        for self_obj in self:
            sale_obj=self_obj.env[self_obj.cond_model].browse(self_obj.sale_order_id.id if self_obj.cond_model == 'sale.order' else self_obj.sale_order_id.order_line.ids)
            for condition in self_obj:
                format_dict={}
                replaced_text = 'False'
                if condition.ext_vals:
                    condition.report_text = ''
                    format_dict=dict.fromkeys(map(unicode.strip, condition.ext_vals.split(',')))
                    for line in sale_obj:
                        for key in format_dict:
                            format_dict[key] = line[key] if key in sale_obj else False
                        format_dict['result'] = condition.python_condition(line, condition.condition_python.format(**format_dict)) if condition.condition_python else False
                        try:
                            condition.report_text += re.sub(replaced_text, '', condition.term_text.format(**format_dict)) if condition.false_replace else condition.term_text.format(**format_dict)
                        except Exception as inst:
                            condition.report_text = 'Error: '+ str(inst)
                elif condition.condition_python:
                    format_dict['result'] = condition.python_condition(condition, condition.condition_python)
                    try:                   
                        condition.report_text += re.sub(replaced_text, '', condition.term_text.format(**format_dict)) if condition.false_replace else condition.term_text.format(**format_dict)                  
                    except Exception as inst:
                        condition.report_text = 'Error: '+ str(inst)
                else:
                    condition.report_text = condition.term_text

    def python_condition(self, obj, condition, context=None):
        company = self.env.user.company_id
        localdict = {'company':company, 'model':obj, 'datetime':datetime, 're':re, 'dt':dt, 'numeral':numeral, 'round':round, 'math':math}
        safe_eval(condition, localdict, mode="exec", nocopy=True)
        return localdict['result'] or ''

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    sale_contract_doc_ids = fields.One2many('sale.contract.doc', 'sale_order_id', string = 'Contract and documents', readonly = True, states = {'draft':[('readonly', False)], 'sent':[('readonly', False)], 'sale':[('readonly', False)], 'done':[('readonly', False)]}, help = "Documents and contract")
    contract_number = fields.Char('Contract number', help = "Contract number", readonly=True, states = {'draft':[('readonly', False)], 'sent':[('readonly', False)], 'sale':[('readonly', False)], 'done':[('readonly', False)]}, default=lambda self: _('New'))
    contract_date = fields.Date(string='Contract date', readonly=True,  states = {'draft':[('readonly', False)], 'sent':[('readonly', False)], 'sale':[('readonly', False)], 'done':[('readonly', False)]}, default=lambda self: fields.Date.today(), help = "Contract date")

  
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or 'New'
#MY NEW ROW START
            vals['contract_number']=int(re.findall('\d+',vals['name'])[0])
#MY NEW ROW END
        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result

