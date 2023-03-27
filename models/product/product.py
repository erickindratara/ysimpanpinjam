# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _


class YudhaProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"
    _description = "This is inherit product template"

    subs_product_ids = fields.One2many('substitute.product', 'product_temp_id',
                                       string='Substitute Product')
    halal_number = fields.Char('No. Halal')
    halal_info = fields.Boolean('Halal Information')
    halal_line_ids = fields.One2many('product.halal.line', 'product_tmpl_id',
                                     string='Halal Information Line')


class YudhaHalalLine(models.Model):
    _name = 'product.halal.line'
    _description = 'Product Halal Line'

    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    halal_number = fields.Char('No. Halal')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    halal_image = fields.Binary('Halal Image')
