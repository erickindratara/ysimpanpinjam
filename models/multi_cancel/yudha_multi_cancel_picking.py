# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError, Warning

class yudha_multi_cancel_picking(models.Model):
    _inherit = "stock.picking"

    def batal_stock_picking(self):
        for move in self.move_lines:
            if move.product_id.type == 'product' or  move.product_id.type == 'consu':
                lot_id = False
                for lot in move.move_line_ids:
                    lot_id = lot.lot_id
                if move.picking_id.picking_type_id.code == 'outgoing':
                    if move.product_id.tracking == 'none':
                        vals = {
                            'product_id': move.product_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'product_uom': move.product_id.uom_id.id,
                            'picking_id': False,
                            'state': 'draft',
                            'date_expected': fields.Datetime.now(),
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': move.location_id.id,
                            'picking_type_id': False,
                            'warehouse_id': self.picking_type_id.warehouse_id.id,
                            'origin_returned_move_id': False,
                            'procure_method': 'make_to_stock',
                        }
                        in_move = move.copy(vals)
                        in_move.write({'reference': self.name})
                        in_move._action_confirm()
                        in_move._action_assign()
                        for j in in_move.move_line_ids:
                            j.unlink()
                        for i in move.move_line_ids:
                            a = self.env['stock.move.line'].create({
                                'move_id': in_move.id,
                                'product_id': in_move.product_id.id,
                                'product_uom_id': in_move.product_uom.id,
                                'location_id': in_move.location_id.id,
                                'location_dest_id': in_move.location_dest_id.id,
                                'picking_id': False,
                                'qty_done': i.qty_done
                            })

                        in_move._action_done()
                    else:
                        vals = {
                            'product_id': move.product_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'product_uom': move.product_id.uom_id.id,
                            'picking_id': False,
                            'state': 'draft',
                            'date_expected': fields.Datetime.now(),
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': move.location_id.id,
                            'picking_type_id': False,
                            'warehouse_id': self.picking_type_id.warehouse_id.id,
                            'origin_returned_move_id': False,
                            'procure_method': 'make_to_stock',
                        }
                        in_move = move.copy(vals)
                        in_move.write({'reference': self.name})
                        in_move._action_confirm()
                        in_move._action_assign()
                        for j in in_move.move_line_ids:
                            j.unlink()
                        for i in move.move_line_ids:
                            a = self.env['stock.move.line'].create({
                                'move_id': in_move.id,
                                'product_id': in_move.product_id.id,
                                'product_uom_id': in_move.product_uom.id,
                                'location_id': in_move.location_id.id,
                                'location_dest_id': in_move.location_dest_id.id,
                                'picking_id': False,
                                'lot_id': i.lot_id.id,
                                'qty_done': i.qty_done
                            })
                        in_move._action_done()
                elif move.picking_id.picking_type_id.code == 'incoming':
                    if move.product_id.type=='consu':
                        if move.product_id.tracking == 'none':
                            vals = {
                                'product_id': move.product_id.id,
                                'product_uom_qty': move.product_uom_qty,
                                'product_uom': move.product_id.uom_id.id,
                                'picking_id': False,
                                'state': 'draft',
                                'date_expected': fields.Datetime.now(),
                                'location_id': move.location_dest_id.id,
                                'location_dest_id': move.location_id.id,
                                'picking_type_id': False,
                                'warehouse_id': self.picking_type_id.warehouse_id.id,
                                'origin_returned_move_id': False,
                                'procure_method': 'make_to_stock',
                            }
                            in_move = move.copy(vals)
                            in_move.write({'reference': self.name})
                            in_move._action_confirm()
                            in_move._action_assign()
                            for j in in_move.move_line_ids:
                                j.unlink()
                            for i in move.move_line_ids:
                                a = self.env['stock.move.line'].create({
                                    'move_id': in_move.id,
                                    'product_id': in_move.product_id.id,
                                    'product_uom_id': in_move.product_uom.id,
                                    'location_id': in_move.location_id.id,
                                    'location_dest_id': in_move.location_dest_id.id,
                                    'picking_id': False,
                                    'qty_done': i.qty_done
                                })

                            in_move._action_done()
                        else:
                            vals = {
                                'product_id': move.product_id.id,
                                'product_uom_qty': move.product_uom_qty,
                                'product_uom': move.product_id.uom_id.id,
                                'picking_id': False,
                                'state': 'draft',
                                'date_expected': fields.Datetime.now(),
                                'location_id': move.location_dest_id.id,
                                'location_dest_id': move.location_id.id,
                                'picking_type_id': False,
                                'warehouse_id': self.picking_type_id.warehouse_id.id,
                                'origin_returned_move_id': False,
                                'procure_method': 'make_to_stock',
                            }
                            in_move = move.copy(vals)
                            in_move.write({'reference': self.name})
                            in_move._action_confirm()
                            in_move._action_assign()
                            for j in in_move.move_line_ids:
                                j.unlink()
                            for i in move.move_line_ids:
                                a = self.env['stock.move.line'].create({
                                    'move_id': in_move.id,
                                    'product_id': in_move.product_id.id,
                                    'product_uom_id': in_move.product_uom.id,
                                    'location_id': in_move.location_id.id,
                                    'location_dest_id': in_move.location_dest_id.id,
                                    'picking_id': False,
                                    'lot_id': i.lot_id.id,
                                    'qty_done': i.qty_done
                                })
                            in_move._action_done()
                    else:
                        if move.product_id.tracking == 'none':
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id),
                                 ('lot_id', '=', lot_id.id)], limit=1)
                            quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done)
                        else:
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id)],
                                limit=1)
                            quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done,
                                                             lot_id)
                elif move.picking_id.picking_type_id.code == 'internal':
                    if move.product_id.type=='consu':
                        if move.product_id.tracking == 'none':
                            vals = {
                                'product_id': move.product_id.id,
                                'product_uom_qty': move.product_uom_qty,
                                'product_uom': move.product_id.uom_id.id,
                                'picking_id': False,
                                'state': 'draft',
                                'date_expected': fields.Datetime.now(),
                                'location_id': move.location_dest_id.id,
                                'location_dest_id': move.location_id.id,
                                'picking_type_id': False,
                                'warehouse_id': self.picking_type_id.warehouse_id.id,
                                'origin_returned_move_id': False,
                                'procure_method': 'make_to_stock',
                            }
                            in_move = move.copy(vals)
                            in_move.write({'reference': self.name})
                            in_move._action_confirm()
                            in_move._action_assign()
                            # for j in in_move.move_line_ids:
                            #     j.unlink()
                            for i in move.move_line_ids:
                                a = self.env['stock.move.line'].create({
                                    'move_id': in_move.id,
                                    'product_id': in_move.product_id.id,
                                    'product_uom_id': in_move.product_uom.id,
                                    'location_id': in_move.location_id.id,
                                    'location_dest_id': in_move.location_dest_id.id,
                                    'picking_id': False,
                                    'qty_done': i.qty_done
                                })

                            in_move._action_done()
                        else:
                            vals = {
                                'product_id': move.product_id.id,
                                'product_uom_qty': move.product_uom_qty,
                                'product_uom': move.product_id.uom_id.id,
                                'picking_id': False,
                                'state': 'draft',
                                'date_expected': fields.Datetime.now(),
                                'location_id': move.location_dest_id.id,
                                'location_dest_id': move.location_id.id,
                                'picking_type_id': False,
                                'warehouse_id': self.picking_type_id.warehouse_id.id,
                                'origin_returned_move_id': False,
                                'procure_method': 'make_to_stock',
                            }
                            in_move = move.copy(vals)
                            in_move.write({'reference': self.name})
                            in_move._action_confirm()
                            in_move._action_assign()
                            for j in in_move.move_line_ids:
                                j.unlink()
                            for i in move.move_line_ids:
                                a = self.env['stock.move.line'].create({
                                    'move_id': in_move.id,
                                    'product_id': in_move.product_id.id,
                                    'product_uom_id': in_move.product_uom.id,
                                    'location_id': in_move.location_id.id,
                                    'location_dest_id': in_move.location_dest_id.id,
                                    'picking_id': False,
                                    'lot_id': i.lot_id.id,
                                    'qty_done': i.qty_done
                                })
                            in_move._action_done()
                    else:
                        if move.product_id.tracking == 'none':
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_id.id),
                                 ('lot_id', '=', lot_id.id)], limit=1)
                            quant._update_available_quantity(move.product_id, move.location_id, move.quantity_done)
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id),
                                 ('lot_id', '=', lot_id.id)], limit=1)
                            quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done)
                        else:
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_id.id)],
                                limit=1)
                            quant._update_available_quantity(move.product_id, move.location_id, move.quantity_done, lot_id)
                            quant = self.env['stock.quant'].search(
                                [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id)],
                                limit=1)
                            quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done,                                                         lot_id)
            move.sudo()._action_cancel()
            journal_rec = self.env['account.move'].sudo().search([('stock_move_id', '=', move.id)], order="id desc")
            for alljur in journal_rec:
                alljur.button_cancel()
        self.write({'state': 'cancel'})
        return

class yudha_multi_cancel_stock_move_line(models.Model):
    _inherit = "stock.move.line"

    cancel_remark = fields.Char(String="Cancel Remarks")

    def unlink(self):
        flag = True
        if not any(line.move_id.picking_id or line.move_id.inventory_id for line in self):
            flag = False
        moves = self.mapped('move_id')
        if flag == False :
            if moves:
                moves._recompute_state()
            res = super(yudha_multi_cancel_stock_move_line, self).unlink()
            return res

class yudha_multi_cancel_stock_move(models.Model):
    _inherit = "stock.move"



    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.reference
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
            })
            new_account_move.post()

    def _action_cancel(self):
        # custom code
        flag = True
        if not any(move.picking_id or move.inventory_id for move in self):
            flag = False
        if flag == False:
            if any(move.state == 'done' for move in self):
                raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
        # custom code

        for move in self:
            if move.state == 'cancel':
                continue
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True

    def _do_unreserve(self):
        flag = True
        if not any(move.picking_id or move.inventory_id for move in self):
            flag = False
        if flag == False:
            super(yudha_multi_cancel_stock_move, self)._do_unreserve()

    def action_cancel(self):
        flag = True
        if not any(move.picking_id or move.inventory_id for move in self):
            flag = False
        if flag == False:
            if any(move.state == 'done' for move in self):
                raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
        for move in self:
            if move.state == 'cancel':
                continue
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



