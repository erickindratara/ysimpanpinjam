# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from  datetime import datetime
from odoo.exceptions import UserError,Warning


class yudha_multi_backdate_StockMoveUpdate(models.Model):
    _inherit = 'stock.move'

    remark = fields.Char(String="Remarks", copy=False)
    transfer_date = fields.Datetime(String="Transfer Date", copy=False)

    def _action_done(self, cancel_backorder=False):
        res = super(yudha_multi_backdate_StockMoveUpdate, self)._action_done()
        for move in res:
            move.write({'date': move.transfer_date or fields.Datetime.now()})
            for line in move.mapped('move_line_ids'):
                line.write({'date': move.transfer_date or fields.Datetime.now()})
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self.transfer_date or self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
            })
            new_account_move.post()# -*- coding : utf-8 -*-


class yudha_multi_backdate_StockMoveLineUpdate(models.Model):
    _inherit = 'stock.move.line'

    remark = fields.Char(String="Remarks", copy=False)
    transfer_date = fields.Datetime(String="Transfer Date", copy=False)
