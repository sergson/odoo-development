# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import UserError

class procurement_order_inh(osv.osv):
    _inherit = "procurement.order"

    def unlink(self, cr, uid, ids, context=None):
        all_users = self.pool.get('res.users')
        user_name = all_users.browse(cr, uid, uid, context=context).name
        alowed_users = ['Administrator']
        procurements = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in procurements:
            if s['state'] == 'cancel':
                if user_name in alowed_users:
                    unlink_ids.append(s['id'])
            else:
                if user_name not in alowed_users:
                    raise UserError(_('Cannot delete Procurement Order(s) which are in %s state.') % s['state'])
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
