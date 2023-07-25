# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, models
from openerp.tools.translate import _
from openerp.exceptions import UserError

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def unlink(self):
        all_users = self.pool.get('res.users')
        cr = self._cr
        uid = self._uid
        context = None
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'purchase.group_purchase_manager'
        admins = ['Administrator']
        if user_name not in admins or not all_users.has_group(cr, uid, managers_group):
            raise UserError(_('Cannot delete a purchase order without some permissions'))
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a purchase order, you must cancel it first.'))
        return super(PurchaseOrderInherit, self).unlink()

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        all_users = self.pool.get('res.users')
        cr = self._cr
        uid = self._uid
        context = None
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'purchase.group_purchase_manager'
        admins = ['Administrator']

        for line in self:
            if line.order_id.state in ['approved', 'done']:
                if user_name not in admins:
                    raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') %(line.state,))
                elif all_users.has_group(cr, uid, managers_group):
                    raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'. '
                                      'You must change state before deleting.') %(line.state,))
                else:
                    raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))
            for proc in line.procurement_ids:
                proc.message_post(body=_('Purchase order line deleted.'))
            line.procurement_ids.filtered(lambda r: r.state != 'cancel').write({'state': 'exception'})
        return super(PurchaseOrderLineInherit, self).unlink()
