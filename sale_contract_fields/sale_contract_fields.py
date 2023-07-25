# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 CodUP (<http://codup.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp import api

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'delegate': fields.char('Delegate'),
        'delegate_parental_case': fields.char('Delegate parental case'),
        'delegate_initials': fields.char('Delegate initials', compute = '_initials'),
        'delegate_role': fields.char('Delegate role'),
        'delegate_role_parent_case': fields.char('Parent case delegate role'),        
        'foundation_id': fields.many2one('res.partner.foundation', 'Foundation'),
        'full_name':fields.char('full_name'),
    }

    @api.depends('delegate')
    def _initials(self):
        for delegate_item in self:
            if delegate_item.delegate:
                fio = delegate_item.delegate
                delegate_item.delegate_initials = (''.join([inits[0:1]+'.' for inits in fio.split()[1:]])+' '+fio.split()[0]).strip()

class res_partner_foundation(osv.osv):
    _name = 'res.partner.foundation'

    _columns = {
        'name': fields.char('Name'),
        'name_parental_case': fields.char('Name parental case'),
        'partner_id': fields.one2many('res.partner', 'foundation_id', sting='Partner')
    }

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'

    _columns = {
        'name_parental_case': fields.char('Parental case name'),
        'foundation_id': fields.many2one('res.users.foundation', 'Foundation'),
        'saleman_initials': fields.char('Saleman initials', compute = '_initials'),
        'saleman_role': fields.char('Saleman role'),
        'saleman_role_parent_case': fields.char('Parent case saleman role'),
    }

    @api.depends('name')
    def _initials(self):
        for name_item in self:
            if name_item.name:
                fio = name_item.name
                name_item.saleman_initials = (''.join([inits[0:1]+'.' for inits in fio.split()[1:]])+' '+fio.split()[0]).strip()

class res_users_foundation(osv.osv):
    _name = 'res.users.foundation'

    _columns = {
        'name': fields.char('Name'),
        'name_parental_case': fields.char('Name parental case'),
        'partner_id': fields.one2many('res.users', 'foundation_id', sting='User')
    }

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'

    _columns = {
        'description_estimate_text': fields.text('Estimate text',
            help="A description of the estimate."),
        'description_estimate_python': fields.text('Estimate python code',
            help="A calculated description of the estimate by python code."),
        'description_technical_task_text': fields.text('Techical task text',
            help="A description of the technical task."),
        'description_technical_task_python': fields.text('Techical task python code',
            help="A calculated description of the technical task."),
    }


