# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError

class Couriers(models.Model):

    _name = "courier.couriers"
    _description = "Couriers"
    _order = "name"

    name = fields.Char(string='Courier name', readonly=False, required=True, copy=False)
    courier_id = fields.Many2one('res.users', string="Courier", required=True, 
        default=lambda self: self.env['res.users'].search([('user_id', '=', self.env.uid)], limit=1), ondelete='set null')
    email = fields.Char(string='Email to send task', help='Courier email addres to send task description', require=True, readonly=False)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='Active', default = True)


class CourierTasks(models.Model):

    _name = "courier.tasks"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Courier tasks"
    _order = "create_date desc"

    name = fields.Char(string='Task description', readonly=True, required=True, states={'draft': [('readonly', False)]}, copy=False)
    active = fields.Boolean(string='Active', readonly = True, default = True, states={'done': [('readonly', False)], 'cancel':[('readonly', False)]})
    courier = fields.Many2one('courier.couriers', string="Courier", required=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='set null')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    state = fields.Selection([('draft', 'To do'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')
                              ], string='Status', index=True, readonly=True, task_actions='onchange', copy=False, default='draft', required=True,
        help='When the task is created the status is \'To do\', task description will sent to courier by e-mail\n\
            If the courier have done the task, the status is \'Done\'.\n\
            If the task is wrong, courier may cancel task without doing')
    date_done = fields.Date(readonly=True, states={'draft': [('readonly', False)]}, string="Date of task have finished", copy = False)
    hours = fields.Float(string='Hours to doing task', digits=(3,1), help='You may set time in hours spended by task before have set status to \'done\'.',
        default=0, readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    dist = fields.Float(string='Distance traveled', digits=(4,0), help='You may set distance in km traveled for task before have set status to \'done\'.',
        default=0, readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    def _add_followers(self):
        user_ids = []
        follower = self.courier.courier_id
        if follower:
            user_ids.append(follower.id)
        self.sudo().message_subscribe_users(user_ids=user_ids)

    @api.model
    def create(self, vals):
        courier_task = super(CourierTasks, self).create(vals)
        if vals.get('courier'):
            courier_task._add_followers()
        return courier_task

    @api.multi
    def write(self, vals):
        res = super(CourierTasks, self).write(vals)
        if vals.get('courier'):
            self._add_followers()
        self.env['mail.template'].browse(self.env.ref('courier_tasks.courier_task').id).send_mail(self.id, force_send=True)
        return res

    @api.multi
    def unlink(self):
        if self.state not in ['draft']:
            raise UserError(_('You can only delete draft task!'))
        return super(CourierTasks, self).unlink()

    @api.multi
    def done_task(self):
        if self.state != 'draft':
            raise UserError(_("You can only submit draft task!"))
        self.write({'state': 'done'})

    @api.multi
    def cancel_task(self):
        self.write({'state': 'cancel'})

    @api.multi
    def reset_task(self):
        self.write({'state': 'draft'})

