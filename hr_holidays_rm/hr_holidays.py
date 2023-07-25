# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from openerp.osv import fields, osv
from openerp import models
from openerp.exceptions import UserError
from openerp.tools.translate import _


class hr_holidays_rm(osv.osv):
    _inherit = "hr.holidays"

    def unlink(self, cr, uid, ids, context=None):
        all_users = self.pool.get('res.users')
        if all_users.has_group(cr, uid, 'base.group_hr_manager'):
            return models.Model.unlink(self, cr, uid, ids, context)
        else:
            for rec in self.browse(cr, uid, ids, context=context):
                if rec.state not in ['draft', 'cancel', 'confirm']:
                    raise UserError(_('You cannot delete a leave which is in %s state.') % (rec.state,))
            return super(hr_holidays_rm, self).unlink(cr, uid, ids, context)
