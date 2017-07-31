# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _


class sale_kit_wizard(models.TransientModel):
    _name = "sale.kit.wizard"
    _description = 'Wizard to select kit for sale order'

    kit_id = fields.Many2one('sale.kit', string = 'Kit name', required = True, help = "Select kit to add to sale order")

    @api.multi
    def kit_return(self, context=None):
        sale_order_id = context.get('sale_order_id')
        if sale_order_id and self.kit_id:
            sale_order_obj=self.env['sale.order'].browse(sale_order_id)
            vals = {
                'note':self.kit_id.note
            }
            sale_order_obj.write(vals)
            for line in self.kit_id.kit_lines:
                vals = {
                    'order_id' : sale_order_id,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id
                }
                sale_order_line = self.env['sale.order.line'].create(vals)
            return True
        else:
            return False

class sale_tokit_wizard(models.TransientModel):
    _name = "sale.tokit.wizard"
    _description = 'Wizard to add sale order linels to kit'

    kit_name =fields.Char(string='Kit name', required=True) 
 
    @api.multi
    def sale_order_lines_to_kit(self, context=None):
        sale_order_id=context.get('sale_order_id')
        sale_order_obj=self.env['sale.order'].browse(sale_order_id)
        kit_note=sale_order_obj.note
        if kit_note and self.kit_name:
            vals = {
                'name': self.kit_name,
                'note': kit_note
            }
            kit = self.env['sale.kit'].create(vals)
            for line in sale_order_obj.order_line:
                vals_lines = {
                    'product_id':line.product_id.id,
                    'product_uom':line.product_uom.id,
                    'sale_kit_id':kit.id,
                    'sequence':line.sequence,
                }
                kit_lines= self.env['sale.kit.lines'].create(vals_lines)

        else:
            raise Warning(_('Add name and note to use it for kit name and note'))
            return False
        return True

