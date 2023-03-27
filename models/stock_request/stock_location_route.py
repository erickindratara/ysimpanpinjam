# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, models, _
from odoo.exceptions import ValidationError


class Yudha_StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    @api.constrains('company_id')
    def _check_company_stock_request(self):
        if any(rec.company_id and self.env['stock.request'].search(
                [('company_id', '!=', rec.company_id.id),
                 ('route_id', '=', rec.id)], limit=1) for rec in self):
            raise ValidationError(
                _('You cannot change the company of the route, as it is '
                  'already assigned to stock requests that belong to '
                  'another company.'))
