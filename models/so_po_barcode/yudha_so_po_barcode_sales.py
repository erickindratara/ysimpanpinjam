# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class yudha_so_po_barcodes_sale_order(models.Model):
    _inherit = 'sale.order'
    _barcode_scanned = fields.Char("Barcode Scanned", help="Value of the last barcode scanned.", store=False)

    @api.onchange('_barcode_scanned')
    def _on_barcode_scanned(self):
        barcode = self._barcode_scanned
        if barcode:
            self._barcode_scanned = ""
            return self.on_barcode_scanned(barcode)

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(
            ['|',('barcode', '=', barcode),('default_code', '=', barcode)]
            , limit=1)
        if product:
            order_lines = self.order_line.filtered(
                lambda r: r.product_id == product)
            if order_lines:
                order_line = order_lines[0]
                qty = order_line.product_uom_qty
                order_line.product_uom_qty = qty + 1
            else:
                newId = self.order_line.new({
                    'product_id': product.id,
                    'product_uom_qty': 1,
                    'price_unit': product.lst_price
                })
                self.order_line += newId
                newId.product_id_change()
        else:
            raise UserError(
                _('Scanned barcode %s is not related to any product.') %
                barcode)
