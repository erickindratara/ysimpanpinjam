# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    Yudha_background = fields.Binary(string="Home Menu Background Image", attachment=True)
    style = fields.Selection([('default', 'Default'), ('left', 'Left'), ('right', 'Right'), ('middle', 'Middle')],default='default', help='Select Background Theme')
