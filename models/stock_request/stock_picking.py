# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_request_ids = fields.One2many(comodel_name='stock.request',
                                        string='Stock Requests',
                                        compute='_compute_stock_request_ids')
    stock_request_count = fields.Integer('Stock Request #',
                                         compute='_compute_stock_request_ids')

    @api.depends('move_lines')
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.move_lines.mapped('stock_request_ids')
            rec.stock_request_count = len(rec.stock_request_ids)

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env.ref(
            'stock_request.action_stock_request_form').read()[0]

        requests = self.mapped('stock_request_ids')
        if len(requests) > 1:
            action['domain'] = [('id', 'in', requests.ids)]
        elif requests:
            action['views'] = [
                (self.env.ref('stock_request.view_stock_request_form').id,
                 'form')]
            action['res_id'] = requests.id
        return action
