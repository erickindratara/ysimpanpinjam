# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_round

class yudha_multi_cancel_account_move(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        self.write({'state': 'cancel'})
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: