# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from reportlab.graphics.barcode import getCodes


class StockRequestKanban(models.Model):
    _name = 'stock.request.kanban'
    _description = 'Stock Request Kanban'
    _inherit = 'stock.request.abstract'

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.request.kanban')
        return super().create(vals)

    @api.model
    def get_barcode_format(self):
        return 'Standard39'

    @api.model
    def _recompute_barcode(self, barcode):
        bcc = getCodes()[self.get_barcode_format()](value=barcode[:-1])
        bcc.validate()
        bcc.encode()
        if bcc.encoded[1:-1] != barcode:
            raise ValidationError(_('CRC is not valid'))
        return barcode[:-1]

    @api.model
    def search_barcode(self, barcode):
        recomputed_barcode = self._recompute_barcode(barcode)
        return self.env['stock.request.kanban'].search([
            ('name', '=', recomputed_barcode)
        ])
