from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    category_id = fields.Selection([('Anggota', 'ANGGOTA'), ('Non Anggota', 'NON ANGGOTA')], string='Kategory Product',help='Kategory Product')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    category_id = fields.Selection([('Anggota', 'ANGGOTA'), ('Non Anggota', 'NON ANGGOTA')], string='Kategory Product',help='Kategory Product')
