# -*- coding: utf-8 -*-
import re

from openerp import api
from openerp import models
from openerp import tools
import logging
import chardet
import codecs

_logger = logging.getLogger(__name__)


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    @api.model
    def _debrand(self, source):
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        params = self.env['ir.config_parameter'].get_debranding_parameters()
        new_name = params.get('web_debranding.new_name')
        new_website = params.get('web_debranding.new_website')

        # We must exclude the case when after the word "odoo" is the word "define".
        # Since JS functions are also contained in the localization files.
        # Example:
        # po file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/i18n/ru.po#L853
        # xml file: https://github.com/odoo/odoo/blob/9.0/addons/im_livechat/views/im_livechat_channel_templates.xml#L148
        try:
            if not isinstance(source, unicode):
                source=unicode(source, 'utf8')
        except Exception as inst:
            _logger.debug("Debranding translate error in source to unicode: "+str(inst))

        try:
            if not isinstance(new_name, unicode):
                new_name=unicode(new_name, 'utf8')
        except Exception as inst:
            _logger.debug("Debranding translate error in new_name to unicode: "+str(inst))

        try:
            if not isinstance(new_website, unicode):
                new_website=unicode(new_website, 'utf8')
        except Exception as inst:
            _logger.debug("Debranding translate error in new_website to unicode: "+str(inst))

	try:
            source = re.sub(unicode(r'\bodoo.com\b', 'utf8'), new_website, source, flags=re.IGNORECASE)
        except Exception as inst:
            _logger.debug("Debranding translate error in re.sub for source or new_website vars: "+str(inst))
            
        try:
            source = re.sub(unicode(r'\bodoo(?!\.define)\b', 'utf8'), new_name, source, flags=re.IGNORECASE)
        except Exception as inst:
            _logger.debug("Debranding translate error in re.sub for source or new_name: "+str(inst))

        return source

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, name, types, lang, source, res_id):
        res = super(IrTranslation, self).__get_source(name, types, lang, source, res_id)
        return self._debrand(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_string(self, model_name):
        res = super(IrTranslation, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_help(self, model_name):
        res = super(IrTranslation, self).get_field_help(model_name)
        return self._debrand_dict(res)
