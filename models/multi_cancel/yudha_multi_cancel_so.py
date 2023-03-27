# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import models, fields, _, api
import odoo
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class yudha_multi_cancel_sale_order(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        # super(abi_StockPickingUpdate, self).button_validate()
        view = self.env.ref('yudha_simpan_pinjam.yudha_multi_cancel_view_change_invadjust_item')
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'change.rubah.info',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': False,
            'context': {'picking_id': self.id},
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
