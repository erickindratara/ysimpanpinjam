# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_round

class yudha_multi_cancel_rubahinfo(models.TransientModel):
    _name = "change.rubah.info"
    _description = "Change Inventory Info"

    cancel_remark = fields.Char(String="Cancel Remarks")

    def Apply_Changes(self):
        active_model = self._context.get('active_model')
        picking_ids = False
        picking_ida = False
        if active_model == 'sale.order':
            sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
            picking_list = [sale_id.picking_ids.ids for sale_id in sale_order_ids][0]
            picking_ids = self.env['stock.picking'].browse(picking_list)
            for picking in sale_order_ids.picking_ids:
                if picking.state != 'cancel':
                    picking.batal_stock_picking()
            for invoice in sale_order_ids.invoice_ids:
                if invoice.state != 'cancel':
                    invoice.button_cancel()
            sale_order_ids.write({'state': 'cancel'})
        elif active_model == 'purchase.order':
            po_ids = self.env['purchase.order'].browse(self._context.get('active_ids'))
            picking_list = [sale_id.picking_ids.ids for sale_id in po_ids][0]
            picking_ids = self.env['stock.picking'].browse(picking_list)
            for order in po_ids:
                for picking in order.picking_ids:
                    if picking.state != 'cancel':
                        picking.batal_stock_picking()
                for invoice in order.invoice_ids:
                    if invoice.state != 'cancel':
                        invoice.button_cancel()
                if order.state in ('draft', 'sent', 'to approve'):
                    for order_line in order.order_line:
                        if order_line.move_dest_ids:
                            siblings_states = (order_line.move_dest_ids.mapped('move_orig_ids')).mapped('state')
                            if all(state in ('done', 'cancel') for state in siblings_states):
                                order_line.move_dest_ids.write({'procure_method': 'make_to_stock'})
                                order_line.move_dest_ids._recompute_state()
                for pick in order.picking_ids.filtered(lambda r: r.state != 'cancel'):
                    pick.action_cancel()
                order.order_line.write({'move_dest_ids': [(5, 0, 0)]})
            po_ids.write({'state': 'cancel'})
        elif active_model == 'stock.picking':
            picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))
            for allpick in picking_ids:
                allpick.batal_stock_picking()
        elif active_model == 'stock.picking.type':
            picking_type_id = self.env['stock.picking.type'].browse(self._context.get('active_id'))
            picking_ids = self.env['stock.picking'].search([('picking_type_id', '=', picking_type_id.id),
                                                            ('state', '!=', 'cancel')], order='id desc', limit=1)
            for allpick in picking_ids:
                allpick.batal_stock_picking()
        elif active_model == 'mrp.production':
            mrp_order_ids = self.env['mrp.production'].browse(self._context.get('active_ids'))
            if mrp_order_ids.state !='cancel':
                for production in mrp_order_ids:
                    production.workorder_ids.filtered(lambda x: x.state != 'cancel').action_cancel()
                    finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    for allmv in (finish_moves | raw_moves):
                        allmv.sudo()._action_cancel()
                        journal_rec = self.env['account.move'].sudo().search([('stock_move_id', '=', allmv.id)], order="id desc")
                        for alljur in journal_rec:
                            alljur.button_cancel()
            mrp_order_ids.write({'state': 'cancel', 'is_locked': True})
        if picking_ids:
            for picking in picking_ids.filtered(lambda x: x.state in ('done', 'cancel')):
                for data in picking.move_line_ids:
                    data.write(
                        {'cancel_remark': self.cancel_remark})
        return
