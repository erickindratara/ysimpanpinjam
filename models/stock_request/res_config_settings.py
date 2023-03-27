# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields, models


class YudhaResConfigSettingss(models.TransientModel):
    _inherit = 'res.config.settings'

    group_stock_request_order = fields.Boolean(
        implied_group='stock.group_stock_manager')

    module_stock_request_purchase = fields.Boolean(
        string='Stock Requests for Purchases')

    module_stock_request_kanban = fields.Boolean(
        string='Stock Requests Kanban integration')
