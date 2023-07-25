#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from datetime import timedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.exceptions import UserError


class hr_payslip_run_rm(osv.osv):

    _inherit = 'hr.payslip.run'
    _order = 'date_start desc, id desc'
    
    
class hr_payslip_rm(osv.osv):

    _inherit = 'hr.payslip'
    _order = 'date_from desc, id desc'
    _columns = {
        'x_all_worked_days_in_period': fields.float('All worked days in period', required=False)
    }
    
    def unlink(self, cr, uid, ids, context=None):
        all_users = self.pool.get('res.users')
        if all_users.has_group(cr, uid, 'base.group_hr_manager'):
            return super(hr_payslip_rm, self).unlink(cr, uid, ids, context)
        else:
            for payslip in self.browse(cr, uid, ids, context=context):
                if payslip.state not in  ['draft','cancel']:
                    raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
            return super(hr_payslip_rm, self).unlink(cr, uid, ids, context)
            

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            #MY ADD START
            if not res:
                try:
                    public_holiday = self.pool.get('hr.holidays.public').is_public_holiday(cr, uid, datetime_day)
                    if public_holiday:
                        res = 'Официальные праздники'
                except:
                    res = False
            #MY ADD END  
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
#MOD BY ME START
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
                 'x_total_days': 0.0,
                 'x_total_hours': 0.0,
                 'x_number_of_worked_holidays': 0.0,
                 'x_number_of_worked_holidays_hours': 0.0,
            }
#MOD BY ME END
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
#MOD BY ME START
                            leaves[leave_type]['number_of_days'] += 0.0
                            leaves[leave_type]['number_of_hours'] += 0.0
#MOD BY ME END              
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
#MY MOD
                                'number_of_days': 0.0,
                                'number_of_hours': 0.0,
#MY ADD START
                                'x_total_days': 0.0,
                                'x_total_hours': 0.0,
#MY ADD END
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
#ADD BY ME
#MY ADD START
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            dYear = day_from.year        #get the year
            dNextMonth = str(int(day_from.month)%12+1)#get next month, watch rollover
            dMonth = day_from.month #get next month, watch rollover
            dDay = "1"                               #first day of next month
            nextMonth =  time.strptime((str(dYear)+'-'+str(dNextMonth)+'-'+str(dDay)),"%Y-%m-%d")#make a datetime obj for 1st of next month
            Month =  datetime.strptime((str(dYear)+'-'+str(dMonth)+'-'+str(dDay)),"%Y-%m-%d")#make a datetime obj for 1st of next month
            eSeconds = time.mktime(nextMonth)
            nextMonth = datetime.fromtimestamp(eSeconds) #make a datetime obj for 1st of next month
            delta = timedelta(seconds=1)    #create a delta of 1 second
            last_day_of_month = nextMonth - delta                 #subtract from nextMonth and return
            day_to = last_day_of_month
            day_from = Month
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                   #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['x_total_days'] += 0.0
                            leaves[leave_type]['x_total_hours'] += 0.0
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 0.0,
                                'number_of_hours': 0.0,
                                'x_total_days': 0.0,
                                'x_total_hours': 0.0,
                                'contract_id': contract.id,
                            }
                    else:
                       #add the input vals to tmp (increment if existing)
                        attendances['x_total_days'] += 1.0
                        attendances['x_total_hours'] += working_hours_on_day

#MYADD END
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res


class hr_payslip_worked_days_rm(osv.osv):
    _inherit = 'hr.payslip.worked_days'
    _columns = {
        'x_total_days': fields.float('Total Number of Days'),
        'x_total_hours': fields.float('Total Number of Hours'),
        'x_number_of_worked_holidays': fields.float('Number of worked holidays'),
        'x_number_of_worked_holidays_hours': fields.float('Number of worked holidays hours'),
    }