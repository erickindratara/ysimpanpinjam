# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import models, fields, api, _


class SubstituteProduct(models.Model):
    _name = 'substitute.product'
    _description = 'Substitute Product'

    product_id = fields.Many2one('product.product', 'Product')
    product_def_code = fields.Char('Internal Reference')
    product_desc = fields.Char('Product Name')
    product_temp_id = fields.Many2one('product.template', 'Product Template ID')

    @api.onchange('product_id')
    def fill_product_details(self):
        if self.product_id:
            self.product_def_code = self.product_id.default_code
            self.product_desc = self.product_id.name
