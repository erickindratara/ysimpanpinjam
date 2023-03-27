# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderBulkConfirm(models.TransientModel):
    """new transient model Purchase Order Bulk Confirm"""
    _name = 'purchase.order.bulk.confirm'
    _description = 'Purchase Order Bulk Confirm'

    def request_confirm_purchase(self):
        """function for confirm multiple PO"""
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        if not active_ids:
            return {'type': 'ir.actions.act_window_close'}
        purchase_orders = self.env['purchase.order'].browse(active_ids)
        #checking state of PO
        states = ['draft', 'sent']
        for order in purchase_orders:
            if order.state not in states:
                raise UserError(_("You cannot confirm "+order.name))
        #confirm/confirm multiple PO for CFO or Manager
        rfq = purchase_orders.filtered(lambda l: l.state in ['draft', 'sent'])
        if rfq:
            rfq.button_confirm()
        return {'type': 'ir.actions.act_window_close'}
