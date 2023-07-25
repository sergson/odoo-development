# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
from openerp.exceptions import UserError, Warning
from openerp.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _

class SaleKit(models.Model):
    _name = "sale.kit"
    _description = 'Kit of lines for sale order'
    _order = "name"

    name = fields.Char('Kit name', help="Name of kit", required=True)
    note = fields.Text(string='Sale order note')
    kit_lines = fields.One2many('sale.kit.lines', 'sale_kit_id', string = 'Kit lines', help="Products for including to kit")

class SaleKitLines(models.Model):
    _name = "sale.kit.lines"
    _description = 'Kit lines'
    _order = "sequence"

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], ondelete='restrict', required=True) 
    product_uom = fields.Many2one('product.uom', string = 'Units of Measure')   
    sale_kit_id = fields.Many2one('sale.kit', string = 'Related kit', ondelete='cascade')
    sequence = fields.Integer(string = 'Sequence')
