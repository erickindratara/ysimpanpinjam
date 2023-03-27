# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields, models

class YudhaProductEcommerce(models.Model):
    _name = "product.ecommerce"
    _description = "Product eCommerce"
    _rec_name = "name"

    name = fields.Char()
