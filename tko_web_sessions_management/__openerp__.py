# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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

{
    'name': 'TKOBR - Odoo Web Sessions Management Rules',
    'version': '2.0.1',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'Sessions timeout and forced termination. Multisession control. Login by calendar (week day hours). Remote IP filter and location.',
    'description': """
# Manage Users Login Rules in Odoo\n
===========================\n
\n
This modules allows the management of logins, by groups or users.\n\n
One can do following:\n
# Group/User Login Configuration:\n
1. Allow multiple sign in of same user;\n
2. Define session timeouts;\n
3. Define a time/week day where users can login;\n
4. You can have user exceptions, overwriting group settings in user settings. The most restrict rule will be applied.\n\n
# Administrator Session Management:\n
1. Sessions log;\n
2. Group by session state, login date time, logout date time, user, group;\n
3. Close any active session.\n\n
# User Session Management:\n
1. Users can see their own log of sessions;\n
2. Users can close related active session;\n
3. Users can choose to close all sessions except current one.\n
NOTE: Admin has no restrictions""",
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    # 'price': 19.99,
    # 'currency': 'EUR',
    'depends': [
        'base',
        'resource',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/scheduler.xml',
        'views/res_users_view.xml',
        'views/res_groups_view.xml',
        'views/ir_sessions_view.xml',
        'views/webclient_templates.xml',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    'auto_install': False,
    'certificate': '',
    'reload': True,
}
