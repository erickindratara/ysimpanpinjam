# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields,models,api,_

class YudhaPurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    rfq_number_ref = fields.Char(string='RFQ No.', compute='_compute_ref_number')
    po_number_ref = fields.Char(string='PO No.', compute='_compute_ref_number')

    @api.depends('purchase_ids')
    def _compute_ref_number(self):
        for data in self:
            text_rfq = ''
            text_po = ''
            for purchase in data.purchase_ids:
                if purchase.state in ['purchase','done']:
                    if text_po:
                        text_po += ', '+purchase.name
                    else:
                        text_po += purchase.name
                elif purchase.state not in ['purchase','done','cancel']:
                    if text_rfq:
                        text_rfq += ', '+purchase.name
                    else:
                        text_rfq += purchase.name
            data.rfq_number_ref = text_rfq
            data.po_number_ref = text_po

class YudhaPurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    description = fields.Char(string='Description')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(YudhaPurchaseRequisitionLine, self)._onchange_product_id()
        if self.product_id:
            name = self.product_id.display_name
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
        return res

class YudhaPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _compute_user_manager_access(self):
        for order in self:
            if order.user_has_groups('purchase.group_purchase_manager'):
                if order.user_has_groups('purchase_3step_approval.group_purchase_cfo'):
                    user_manager_access = False
                else:
                    user_manager_access = True
            else:
                user_manager_access = False
            if user_manager_access and not order.need_double_approve and order.state == 'to approve':
                order.user_manager_access = True
            else:
                order.user_manager_access = False

    user_manager_access = fields.Boolean(compute='_compute_user_manager_access')
    need_double_approve = fields.Boolean(copy=False, readonly=True)

    def button_confirm(self):
        ''' replace function base to change group approve ''' 
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            order.write({'state': 'to approve'})
        return True

    def button_approve_manager(self):
        for order in self:
            if order.state not in ['to approve']:
                continue
            if order.company_id.po_double_validation == 'one_step'\
                or (order.company_id.po_double_validation == 'two_step'\
                    and order.amount_total < self.env.user.company_id.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id,
                        order.company_id, order.date_order or fields.Date.today()))\
                or order.user_has_groups('purchase_3step_approval.group_purchase_cfo'):
                order.button_approve()
            else:
                order.write({'need_double_approve': True})
        return True

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        res = super(YudhaPurchaseOrder, self)._onchange_requisition_id()
        if self.requisition_id and self.requisition_id.user_id:
            self.user_id = self.requisition_id.user_id
        return res

class YudhaPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_purchase_description(self, product_lang):
        name = super(YudhaPurchaseOrderLine, self)._get_product_purchase_description(
            product_lang=product_lang)
        if self.order_id.requisition_id and product_lang:
            for line in self.order_id.requisition_id.line_ids.filtered(
                lambda l: l.product_id.id == product_lang.id):
                name = line.description
        return name
