# -*- coding : utf-8 -*-
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class MyPposOrder(models.Model):
    _inherit = "pos.order"

    is_cust_block = fields.Boolean(string='Customer Block')

    @api.model
    def cek_pinjaman_exist(self,partner):
        if not partner:
            return
        mycek = self.env['yudha.peminjaman.sembako'].search([('partner_id','=',partner)])
        if mycek:
            if mycek.jml_pinjam > 0 :
                return mycek.jml_pinjam
            else:
                return False
        else:
            return False
