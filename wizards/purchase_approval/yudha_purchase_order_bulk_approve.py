# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderBulkApprove(models.TransientModel):
    """new transient model Purchase Order Bulk Approve"""
    _name = 'purchase.order.bulk.approve'
    _description = 'Purchase Order Bulk Approve'

    def request_approve_purchase(self):
        """function for approve multiple PO"""
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        if not active_ids:
            return {'type': 'ir.actions.act_window_close'}
        # purchase_orders = self.env['purchase.order'].browse(active_ids)
        purchase_orders = self.env['purchase.order'].search([('id', 'in', active_ids)], order="id asc")
        #check group cfo
        cfo = self.env.user.has_group('purchase_3step_approval.group_purchase_cfo')

        #checking state of PO
        states = ['draft', 'sent', 'to approve']
        lanjutkan = True
        lognya = ''
        for order in purchase_orders:
            if order.state not in states:
                raise UserError(_("You cannot approve "+order.name))
            if not order.user_manager_access and cfo:
                raise UserError(_("You cannot approve "+order.name+\
                                  ", please ask Purchase Manager to approve first"))
            if order.amount_total > 25000000:
                if not cfo:
                    lognya += '%s ' % (order.name)
                    lanjutkan = False

        if lanjutkan == False:
            raise UserError(_("You are not authorized to approve these PO \n" + \
                              "PO Numbers: " + lognya))
        #confirm/approve multiple PO for CFO or Manager
        rfq = purchase_orders.filtered(lambda l: l.state in ['draft', 'sent'])
        # if rfq:
        #     rfq.button_confirm()
        for r in rfq:
            r.button_confirm()
        toapprove = purchase_orders.filtered(lambda l: l.state == 'to approve')
        # if toapprove:
        #     toapprove.button_approve()
        for t in toapprove:
            t.button_approve()

        return {'type': 'ir.actions.act_window_close'}
