# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import UserError

class hr_timesheet_shee_inh(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"

    def unlink(self, cr, uid, ids, context=None):

        all_users = self.pool.get('res.users')
        if all_users.has_group(cr, uid, 'base.group_hr_manager'):
            sheets = self.read(cr, uid, ids, ['state', 'total_attendance'], context=context)
            for sheet in sheets:
                if sheet['state'] in ('confirm', 'done'):
                    raise UserError(_('You cannot delete a timesheet which is already confirmed.'))
                elif sheet['total_attendance'] != 0.00:
                    raise UserError(_('You cannot delete a timesheet which have attendance entries.'))
            toremove = []
            analytic_timesheet = self.pool.get('account.analytic.line')
            for sheet in self.browse(cr, uid, ids, context=context):
                for timesheet in sheet.timesheet_ids:
                    toremove.append(timesheet.id)
            analytic_timesheet.unlink(cr, uid, toremove, context=context)

            return super(hr_timesheet_shee_inh, self).unlink(cr, uid, ids, context=context)
        else:
            raise UserError(_('Only allowed users can delete timesheet. Contact to: Administrator.'))

