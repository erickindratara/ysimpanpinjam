# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
import time


class yudha_multi_backdate_RemarkItem(models.TransientModel):
    _name = "change.module"
    _description = "Change Module"

    transfer_date = fields.Datetime(String="Transfer Date")
    remark = fields.Char(String="Remarks")

    def action_apply(self):
        active_model = self._context.get('active_model')
        picking_ids = False
        picking_ida = False
        if active_model == 'sale.order':
            sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
            picking_list = [sale_id.picking_ids.ids for sale_id in sale_order_ids][0]
            picking_ids = self.env['stock.picking'].browse(picking_list)
        elif active_model == 'purchase.order':
            sale_order_ids = self.env['purchase.order'].browse(self._context.get('active_ids'))
            picking_list = [sale_id.picking_ids.ids for sale_id in sale_order_ids][0]
            picking_ids = self.env['stock.picking'].browse(picking_list)
        elif active_model == 'stock.picking':
            picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))
        elif active_model == 'stock.picking.type':
            picking_type_id = self.env['stock.picking.type'].browse(self._context.get('active_id'))
            picking_ids = self.env['stock.picking'].search([('picking_type_id', '=', picking_type_id.id),
                                                            ('state', '!=', 'cancel')], order='id desc', limit=1)
        elif active_model == 'mrp.production':
            sale_order_ids = self.env['mrp.production'].browse(self._context.get('active_ids'))
            picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))

        if picking_ids:
            for picking in picking_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
                if not picking.transfer_date:
                    picking.write({'remark': self.remark, 'transfer_date': self.transfer_date})
                for data in picking.move_lines:
                    data.write(
                        {'date': self.transfer_date, 'remark': self.remark, 'transfer_date': self.transfer_date})
                for data in picking.move_line_ids:
                    data.write(
                        {'date': self.transfer_date, 'remark': self.remark, 'transfer_date': self.transfer_date})
            for picking in picking_ids.filtered(lambda x: x.state not in ('cancel')):
                for data in picking.move_lines:
                    data.write({'date': self.transfer_date, 'remark': self.remark, 'transfer_date': self.transfer_date})
                    for line in data.mapped('move_line_ids'):
                        line.write({'date': self.transfer_date or fields.Datetime.now()})
            for transfer in picking_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
                picking_type = transfer.picking_type_id
                precision_digits = transfer.env['decimal.precision'].precision_get('Product Unit of Measure')
                no_quantities_done = all(
                    float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                    transfer.move_line_ids)
                no_reserved_quantities = all(
                    float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for
                    move_line in transfer.move_line_ids)
                if no_reserved_quantities and no_quantities_done:
                    raise UserError(_(
                        'You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

                if picking_type.use_create_lots or picking_type.use_existing_lots:
                    lines_to_check = transfer.move_line_ids
                    if not no_quantities_done:
                        lines_to_check = lines_to_check.filtered(
                            lambda line: float_compare(line.qty_done, 0,
                                                       precision_rounding=line.product_uom_id.rounding)
                        )

                    for line in lines_to_check:
                        product = line.product_id
                        if product and product.tracking != 'none':
                            if not line.lot_name and not line.lot_id:
                                raise UserError(
                                    _('You need to supply a Lot/Serial number for product %s.') % product.display_name)
                # if rec.picking_type_id.code != 'Vendors':
                if no_quantities_done:
                    view = transfer.env.ref('stock.view_immediate_transfer')
                    wiz = transfer.env['stock.immediate.transfer'].create({'pick_ids': [(4, transfer.id)]})
                    return {
                        'name': _('Immediate Transfer?'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.immediate.transfer',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': transfer.env.context,
                    }

                if transfer._get_overprocessed_stock_moves() and not transfer._context.get('skip_overprocessed_check'):
                    view = transfer.env.ref('stock.view_overprocessed_transfer')
                    wiz = transfer.env['stock.overprocessed.transfer'].create({'picking_id': transfer.id})
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.overprocessed.transfer',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': transfer.env.context,
                    }

                # Check backorder should check for other barcodes
                if transfer._check_backorder():
                    return transfer.action_generate_backorder_wizard()
                transfer.action_done()
                return

class yudha_multi_backdate_backorder(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    _description = 'Backorder Confirmation'


    def _process(self, cancel_backorder=False):
        active_model = self._context.get('active_model')
        print('mymodel', active_model)
        if active_model=='stock.picking':
           myid = self.env['stock.picking'].browse(self._context.get('active_ids'))
           print('picking name', myid.name)
           for allid in myid:
               for allpick in self.pick_ids:
                   if allpick.name== allid.name:
                       allid.write({'transfer_date':allid.transfer_date,
                                'remark':allid.remark})
        self.pick_ids.action_done()
        if cancel_backorder:
            for pick_id in self.pick_ids:
                backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
                backorder_pick.action_cancel()
                pick_id.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
