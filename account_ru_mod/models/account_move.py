# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class AccountMoveInherited(models.Model):
    _inherit = "account.move"

    @api.onchange('date')
    def date_to_lines(self):
        if self.state in ['draft']:
            vals = {}
            mod_lines = []
            for line in self.line_ids:
                line_vals = {}
                if self.date != line.date_maturity:
                    line_vals['date_maturity'] = self.date
                    mod_lines.append([1, line.id, line_vals])
                else:
                    mod_lines.append([4, line.id, False])
            if len(mod_lines) > 0:
                vals['line_ids'] = mod_lines
            self.update(vals)
