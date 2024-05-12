# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import UserError


class task_inh(osv.osv):
    _inherit = "project.task"

    def write(self, cr, uid, ids, vals, context=None):
        all_users = self.pool.get('res.users')
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'project.group_project_manager'
        admins = ['Administrator']
        user_group = 'project.group_project_user'
        planned_hours = self.pool.get('project.task').browse(cr, uid, ids, context).planned_hours
        timesheet_ids = self.pool.get('project.task').browse(cr, uid, ids, context).timesheet_ids
        if vals.get('timesheet_ids'):
            unit_amount_list = self.pool['account.analytic.line'].read(cr, uid, timesheet_ids.ids, ['unit_amount'], context)
            unit_amount_list_index = [x['id'] for x in unit_amount_list]
            effective_hours = 0
            for line in vals.get('timesheet_ids'):
                if line[0] in [0]:
                    effective_hours += line[2].get('unit_amount', 0)
                elif line[0] in [1]:
                    if line[2].get('unit_amount') not in [None, False]:
                        effective_hours += line[2].get('unit_amount', 0)
                elif line[0] in [4]:
                    effective_hours += unit_amount_list[unit_amount_list_index.index(line[1])].get('unit_amount')
        remaining_hours = planned_hours - effective_hours
        if remaining_hours < 0:
            raise UserError(_('Затраченное время превышает количество запланированных часов'))
        if user_name in admins:
            pass
        elif all_users.has_group(cr, uid, managers_group):
            if vals.get('planned_hours'):
                raise UserError(_('Недостаточно прав, чтобы изменить запланированное количество часов'))
            if vals.get('partner_id'):
                raise UserError(_('Недостаточно прав, чтобы изменить заказчика'))
            if vals.get('sale_line_id'):
                raise UserError(_('Недостаточно прав, чтобы изменить строку заказа'))
            if vals.get('timesheet_ids'):
                task_user_id = self.pool.get('project.task').browse(cr, uid, ids, context).user_id.id
                if task_user_id != uid:
                    raise UserError(_('Недостаточно прав, чтобы отчитаться по задаче назначенной другому исполнителю'))
            if vals.get('project_id'):
                raise UserError(_('Недостаточно прав, чтобы перевести задачи в другой проект'))
            planned_hours = self.pool.get('project.task').browse(cr, uid, ids, context).planned_hours
            effective_hours = planned_hours - remaining_hours
            if vals.get('user_id') and effective_hours > 0:
                raise UserError(_('Недостаточно прав, чтобы передать задачу по которой имеется отчетность другому исполнителю'))

        elif all_users.has_group(cr, uid, user_group):
            if vals.get('user_id'):
                if vals.get('user_id') != uid:
                    raise UserError(_('Недостаточно прав, чтобы передать задачу другому исполнителю'))
            if vals.get('date_deadline'):
                raise UserError(_('Недостаточно прав, чтобы изменить срок'))
            if vals.get('planned_hours'):
                raise UserError(_('Недостаточно прав, чтобы изменить запланированное количество часов'))
            if vals.get('partner_id'):
                raise UserError(_('Недостаточно прав, чтобы изменить заказчика'))
            if vals.get('sale_line_id'):
                raise UserError(_('Недостаточно прав, чтобы изменить строку заказа'))
            if vals.get('project_id'):
                raise UserError(_('Недостаточно прав, чтобы перевести задачу в другой проект'))
            if vals.get('timesheet_ids'):
                task_user_id = self.pool.get('project.task').browse(cr, uid, ids, context).user_id.id
                if task_user_id != uid:
                    raise UserError(_('Недостаточно прав, чтобы отчитаться по задаче назначенной другому исполнителю'))
        else:
            raise UserError(_('Недостаточно прав для внесения изменений'))
        return super(task_inh, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        all_users = self.pool.get('res.users')
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'project.group_project_manager'
        admins = ['Administrator']
        user_group = 'project.group_project_user'
        if user_name in admins:
            pass
        elif all_users.has_group(cr, uid, managers_group):
            pass
        elif all_users.has_group(cr, uid, user_group):
            raise UserError(_('Недостаточно прав, чтобы удалить задачу'))
        else:
            raise UserError(_('Недостаточно прав для удаления задач'))
        return super(task_inh, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        all_users = self.pool.get('res.users')
        user_name = all_users.browse(cr, uid, uid, context=context).name
        managers_group = 'project.group_project_manager'
        admins = ['Administrator']
        user_group = 'project.group_project_user'
        if user_name in admins:
            pass
        elif all_users.has_group(cr, uid, managers_group):
            pass
        elif all_users.has_group(cr, uid, user_group):
            raise UserError(_('Недостаточно прав, чтобы создать задачу'))
        else:
            raise UserError(_('Недостаточно прав для создания задачи'))
        return super(task_inh, self).create(cr, uid, vals, context)

