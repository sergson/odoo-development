# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.exceptions import UserError
from openerp.tools.translate import _
from datetime import datetime


class procurement_order_rm(osv.osv):
    _inherit = "procurement.order"

    def _get_product_attr(self, cr, uid, product_obj, attr_id, context=None):
        try:
            product_av_obj = product_obj.attribute_value_ids
            attr_value = 1
            for product_av in product_av_obj:
                if product_av.attribute_id.name == attr_id:
                    attr_value = float(product_av.name)
                    break
        except Exception as inst:
            raise UserError(_(inst.args))
        #        else:
        #            raise UserError (_(attr_value))
        return attr_value


    def _convert_qty_company_hours(self, cr, uid, procurement, context=None):
        product_uom = self.pool.get('product.uom')
        company_time_uom_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id
        working_time = self._get_product_attr(cr, uid, procurement.product_id, 'time', context=None)  # Added by me
        if procurement.product_uom.id != company_time_uom_id.id and procurement.product_uom.category_id.id == company_time_uom_id.category_id.id:
            planned_hours = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, company_time_uom_id.id)
        else:
#            planned_hours = procurement.product_qty
# ------------------------------------ #mod by me
            product_base_uom = procurement.product_id.product_tmpl_id.uom_id
            if procurement.product_uom.factor and product_base_uom.factor and product_base_uom.factor != procurement.product_uom.factor:
                planned_hours = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty,
                                                         product_base_uom.id) * working_time
            else:
                planned_hours = procurement.product_qty * working_time
# -----------------------------------
        return round(planned_hours, 1)

    def _task_description_get(self, cr, uid, sale_order, partner):
        description = []
        if sale_order:
            if partner:
                description.append(partner.name)
                description.append(u'<br/>')
                if partner.zip:
                    description.append(partner.zip)
                if partner.city:
                    description.append(u', ' + partner.city)
                if partner.street:
                    description.append(u', ' + partner.street)
                if partner.street2:
                    description.append(u', ' + partner.street2)
                description.append(u'<br/>')
                if partner.phone:
                    description.append(partner.phone)
                if partner.mobile:
                    description.append(u', ' + partner.mobile)
                if partner.fax:
                    description.append(u', ' + partner.fax)
                if partner.email:
                    description.append(u'<br/> E-mail:' + partner.email)
            if sale_order.contract_number and sale_order.contract_date:
                description.append(u'<br/><br/>Договор № ' + sale_order.contract_number + u' от ' + datetime.strptime(
                    sale_order.contract_date, "%Y-%m-%d").strftime("%d.%m.%Y"))
            if sale_order.note:
                description.append(u'<br/><br/>Предмет договора: ' + sale_order.note)

        return ''.join(description)

    def _create_service_task(self, cr, uid, procurement, context=None):
        project_task = self.pool.get('project.task')
        project = self._get_project(cr, uid, procurement, context=context)
        planned_hours = self._convert_qty_company_hours(cr, uid, procurement, context=context)
        task_id = project_task.create(cr, uid, {
            'name': '%s:%s' % (procurement.origin or '', procurement.product_id.name),
            'date_deadline': procurement.date_planned,
            'planned_hours': planned_hours,
            'remaining_hours': planned_hours,
            'partner_id': procurement.sale_line_id and procurement.sale_line_id.order_id.partner_id.id or procurement.partner_dest_id.id,
            'user_id': procurement.product_id.product_manager.id,
            'procurement_id': procurement.id,
#            'description': procurement.name + '<br/>',
            'description': self._task_description_get(cr, uid, procurement.sale_line_id.order_id, (
                        procurement.sale_line_id and procurement.sale_line_id.order_id.partner_id or procurement.partner_dest_id)) + u'<br/><br/>Задача: ' + procurement.name + '\n',
            'project_id': project and project.id or False,
            'company_id': procurement.company_id.id,
        },context=context)
        self.write(cr, uid, [procurement.id], {'task_id': task_id}, context=context)
        self.project_task_create_note(cr, uid, [procurement.id], context=context)
        return task_id
