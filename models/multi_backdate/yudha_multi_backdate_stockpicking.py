# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from datetime import datetime
from odoo import SUPERUSER_ID
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError, Warning


class yudha_multi_backdate_Stock_Picking(models.Model):
    _inherit = 'stock.picking'

    transfer_date = fields.Datetime(String="Transfer Date", copy=False)
    remark = fields.Char(String="Remarks", copy=False)

    def button_validate(self):
        if self.picking_type_id.code == 'outgoing' or self.picking_type_id.code == 'incoming' or self.picking_type_id.code == 'internal':
            self.ensure_one()
            if not self.move_lines and not self.move_line_ids:
                raise UserError(_('Please add some lines to move'))
            #super(abi_StockPickingUpdate, self).button_validate()
            view = self.env.ref('yudha_multi_backdate.yudha_multi_backdate_view_change_stock_item')
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'change.module',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': False,
                'context': {'picking_id': self.id},
            }

        else:
            self.ensure_one()
            res = super(yudha_multi_backdate_Stock_Picking, self).button_validate()
            return res
