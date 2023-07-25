# -*- coding: utf-8 -*- Author be-cloud (Jerome Sonnet) Somme code from OFX importer

import logging
import StringIO
import unicodecsv
import chardet
import codecs
import dateutil.parser
import base64
import hashlib
import re

from openerp import api, fields, models, _
from openerp.exceptions import UserError
#from openerp.osv import expression

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _parse_file(self,data_file):

        # decode Charset and remove BOM if needed
        encoding = chardet.detect(data_file)
#        _logger.debug('ENC_OLD: ' + str(encoding['encoding']))
        data_file.decode(encoding['encoding'])
        if data_file[:3] == codecs.BOM_UTF8:
            data_file = data_file[3:]
        data_file =  data_file.decode(encoding['encoding']).encode('utf-8')
        encoding = chardet.detect(data_file)    
#        _logger.debug('ENC_NEW: ' + str(encoding['encoding']))
        
        # creade lines
        csvfile = StringIO.StringIO(data_file)
        csvlines = csvfile.readlines()

        #crete csv dict
        csv = []
        csvtitle ={}
        csvdoc = {}
        for line in csvlines:
            linetuple = line.partition('=')
            sign1 = ['1CClientBankExchange']
            if any (sign in linetuple[0] for sign in sign1):
                csvtitle = {}
                csvtitle['title'] = '1CClientBankExchange'
            sign2 = 'КонецРасчСчет' 
            if sign2 in linetuple[0]:
                csvtitle['title_end'] = 'КонецРасчСчет'
            sign3 = 'СекцияДокумент'
            if  sign3 in linetuple[0]:
                if 'title_end' in csvtitle:
                    csv.append(csvtitle)
                    csvtitle = {}
                csvdoc = {}
                csvdoc[linetuple[0]] = linetuple[2]
                csvdoc['title'] = '1CClientBankExchange'
            if 'title' in csvtitle:
                if linetuple[0] in csvtitle:
                    if linetuple[0] == 'ДатаНачала':
                        pass
                    if linetuple[0] == 'НачальныйОстаток':
                        pass
                else:
                    csvtitle[linetuple[0]] = linetuple[2]
            sign4 = 'КонецДокумента'
            if sign4 in linetuple[0]:
                csvdoc['doc_end'] = 'КонецДокумента'
                csv.append(csvdoc)
                csvdoc = {}
            if 'СекцияДокумент' in csvdoc:
                csvdoc[linetuple[0]] = linetuple[2]
#        _logger.debug(str(csv))


        if not csv:
            return super(AccountBankStatementImport, self)._parse_file(data_file)
        all_statements = {}
        statement = {}
#        try:
        for line in csv:
                if  line['title'] == '1CClientBankExchange':
                    if not sign3 in line: 
                        currency = 'RUB'
                        account_num = line['РасчСчет']
                        statement_date = dateutil.parser.parse(line['ДатаСоздания'], dayfirst=True, fuzzy=True).date()
                        statement = {
                                'name': 'Выписка '+ line['ДатаНачала']+ ' - ' + line['ДатаКонца'] +' по сч.: ' +line['РасчСчет'],
                                'date': statement_date,
                                'balance_start': float(line['НачальныйОстаток']),
                                'balance_end_real': float(line['КонечныйОстаток']),
                                'transactions':[],
                        }

                    else:
                        m = hashlib.sha512()
                        m.update(str(line))
                        if account_num in line['ПлательщикРасчСчет']:
                            amount_sign = -1
                            partner_inn = line['ПолучательИНН'] if 'ПолучательИНН' in line else False
                            partner_kpp = line['ПолучательКПП'] if 'ПолучательКПП' in line else False
                            partner_name = line['Получатель1'] if 'Получатель1' in line else line['Получатель'] if 'Получатель' in line else false
                            partner_bank_num = line['ПолучательСчет'] if 'ПолучательСчет' in line else False
                            partner_bank_name = line['ПолучательБанк1'] if 'ПолучательБанк1' in line else False
                            partner_bank_city = line['ПолучательБанк2'] if 'ПолучательБанк2' in line else False
                            partner_bank_bik = line ['ПолучательБИК'] if 'ПолучательБИК' in line else False
                            partner_bank_corr = line['ПолучательКорсчет'] if 'ПолучательКорсчет' in line else False
                        elif account_num in line['ПолучательСчет']:
                            amount_sign = 1
                            partner_inn = line['ПлательщикИНН'] if 'ПлательщикИНН' in line else False
                            partner_kpp = line['ПлательщикКПП'] if 'ПлательщикКПП' in line else False
                            partner_name = line['Плательщик1'] if 'Плательщик1' in line else  line['Плательщик'] if 'Плательщик' in line else False
                            partner_bank_num = line['ПлательщикСчет'] if 'ПлательщикСчет' in line else False
                            partner_bank_name = line['ПлательщикБанк1'] if 'ПлательщикБанк1' in line else False
                            partner_bank_city = line['ПлательщикБанк2']if 'ПлательщикБанк2' in line else False
                            partner_bank_bik = line ['ПлательщикБИК'] if 'ПлательщикБИК' in line else False
                            partner_bank_corr = line['ПлательщикКорсчет'] if 'ПлательщикКорсчет' in line else False
                        else:
                            amount_sign = 0
                            partner_inn = ''
                            partner_name = ''
                            partner_kpp = ''
                            partner_bank_num = ''
                            partner_bank_name = ''
                            partner_bank_city = ''
                            partner_bank_bik = ''
                            partner_bank_corr = ''
                            raise UserError(_('Can not find account number: '+ account_num +' in some part of  satement, check it!'))
                        
                        try:
                            if partner_inn: 
                                partner_inn =  re.findall(r'\d+',partner_inn)
                                partner_inn = partner_inn[0] if partner_inn else ''
                            partner_existing = self.env['res.partner'].search([('inn', 'ilike', partner_inn)])
                        except:
                            partner_existing = False
                            partner_inn = False
                        if partner_existing:
                            if len(partner_existing) > 1:
                                partner_existing_more = self.env['res.partner'].search([('inn', '=', partner_inn)])
                                if len(partner_existing_more) > 1:
#                                    raise UserError(_('More than one partner with one same INN have been met, partner finding skipped. INNs: '+partner_existing_more[0].inn))
                                    partner_name = partner_existing_more[0].name
                                    partner = partner_existing_more[0]  
                                elif len(partner_existing_more) == 1:
                                    partner_name = partner_existing_more[0].name
                                    partner = partner_existing_more[0]
                            elif len(partner_existing) == 1:
                                partner_name = partner_existing[0].name
                                partner = partner_existing[0]
                        elif partner_name:
                            partner_existing = self.env['res.partner'].search([('name', 'ilike', partner_name)])
                            if len(partner_existing) > 1:
                                partner_existing_more = self.env['res.partner'].search([('name', '=ilike', partner_name)])
                                if len(partner_existing_more) > 1:
                                    raise UserError(_('More than one partner with one same name have been met, partner finding skipped. NAMEs: '+partner_existing_more[0].name))
                                elif len(partner_existing_more) == 1:
                                    partner_name = partner_existing_more[0].name
                                    partner = partner_existing_more[0]
                            elif len(partner_existing) == 1:
                                partner_name = partner_existing[0].name
                                partner = partner_existing[0]
                            else:
                                if amount_sign > 0:
                                    customer =True
                                    supplier = False
                                elif amount_sign < 0:
                                    customer = False
                                    supplier = True
                                if len(partner_inn) > 10:
                                    company_type = 'person'
                                else:
                                    company_type = 'company'
                                partner_vals = {
                                               'company_type': company_type,
                                               'customer': customer,
                                               'supplier': supplier,
                                               'name': partner_name,
                                               'inn': partner_inn,
                                               'kpp': partner_kpp,
                                               'active': True,
                                }
#                                _logger.debug(str(partner_vals))
                                partner_existing =  self.env['res.partner'].create(partner_vals)
                                partner = partner_existing

                        bank_partner_obj = self.env['res.partner.bank']
                        bank_obj = self.env['res.bank']
                        if partner_bank_bik: partner_bank_bik = re.findall(r'\d+',partner_bank_bik)
                        partner_bank_bik = partner_bank_bik[0] if partner_bank_bik else '' 
                        if partner_bank_num: partner_bank_num = re.findall(r'\d+',partner_bank_num)
                        partner_bank_num = partner_bank_num[0] if partner_bank_num else '' 
                        partner_bank = bank_obj.search([('bic', '=', partner_bank_bik)], limit = 1)
                        if not partner_bank:
                            bank_vals = {
                                        'name': partner_bank_name,
                                        'city': partner_bank_city,
                                        'bic': partner_bank_bik,
                                        'corr_acc': partner_bank_corr,
                            }
                            partner_bank = bank_obj.create(bank_vals)

                        partner_bank_partner =  bank_partner_obj.search([('acc_number', '=', partner_bank_num)], limit = 1)
                        if not partner_bank_partner:
                            bank_partner_vals = {
                                                'acc_number':partner_bank_num,
                                                'bank_id':partner_bank.id,
                                                'partner_id': partner.id
                            }
                            partner_bank_partner = bank_partner_obj.create(bank_partner_vals)

                        if any(x in line for x in ['ДатаСписано','ДатаПоступило','Дата']):
                            if len(line['ДатаСписано'])>9:
                                trans_date = dateutil.parser.parse(line['ДатаСписано'], dayfirst=True, fuzzy=True).date()
                            elif len(line['ДатаПоступило'])>9:
                                trans_date = dateutil.parser.parse(line['ДатаПоступило'], dayfirst=True, fuzzy=True).date()
                            elif len(line['Дата'])>9:
                                trans_date = dateutil.parser.parse(line['Дата'], dayfirst=True, fuzzy=True).date()
                        else:
                            trans_date = statement_date
                        vals_line = {
                            'date': trans_date,
                            'name': line['СекцияДокумент'] + ' №' + line['Номер'] + ' от ' + line['Дата'] + '( ' + line['НазначениеПлатежа'] + ' )',
                            'ref': line['СекцияДокумент'] + ' №' + line['Номер'],
                            'amount': float(line['Сумма'])*amount_sign,
                            'unique_import_id': m.hexdigest(),
                            'note': line['СекцияДокумент']+' №'+line['Номер']+' от '+line['Дата']+':'+line['Плательщик']+' '+line['Сумма']+' руб. --->'+line['Получатель']+' '+line['НазначениеПлатежа'],
                            'partner_id': partner.id, 
                            'partner_name': partner_name,
                            'bank_account_id': partner_bank_partner.id,
                        }
#                            'account_number': partner_bank_num,


                        statement['transactions'].append(vals_line)
        all_statements[currency , account_num ] = [statement]                        
#        raise UserError(_(str(all_statements[currency , account_num ])))
#        _logger.debug(str(all_statements[currency , account_num ]))
#        except Exception, e:
#            raise UserError(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))
        return currency, account_num, all_statements[currency , account_num ]

