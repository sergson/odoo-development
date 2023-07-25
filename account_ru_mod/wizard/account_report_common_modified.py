# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AccountCommonReportModified(models.TransientModel):
    _name = "account_ru_mod.common.report"
    _description = "Account Common Report Modified"

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([]))
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    def _print_report(self, data):
        raise (_('Error!'), _('Not implemented.'))

# MY ADD START
    def _build_contexts_before(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = False
        _logger.debug('DATE_FROM: '+str(data['form']['date_from']))
        if data['form']['date_from']:
            result['date_to'] = (datetime.strptime(data['form']['date_from'],'%Y-%m-%d')- relativedelta(days=1)).strftime('%Y-%m-%d')
        else:
            result['date_to'] = False          
        _logger.debug('DATE_TO: '+ str(result['date_to']))
        result['strict_range'] = True if result['date_from'] else False
        return result

    def _build_contexts_full(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = False
        result['date_to'] =data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result
# MY ADD END

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
# MY ADD START
        used_context_before = self._build_contexts_before(data)       
        data['form']['used_context_before'] = dict(used_context_before, lang=self.env.context.get('lang', 'en_US'))

        used_context_full = self._build_contexts_full(data)       
        data['form']['used_context_full'] = dict(used_context_full, lang=self.env.context.get('lang', 'en_US'))
# MY ADD END
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        
        return self._print_report(data)
