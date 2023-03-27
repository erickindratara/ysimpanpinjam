# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import time

SESSION_STATES = [
        ('active', 'Active'),
        ('in active','In Active')
]

class yudha_master_jenis_tabungan(models.Model):
    _name = 'yudha.master.jenis.tabungan'

    name = fields.Char(string='Nama Jenis Tabungan',copy=True, required=True, index=True )
    akun_coa = fields.Many2one('account.account', string='No COA', required=True,index=True)
    biaya_admin = fields.Float('Biaya Admin', digits=(19, 2))
    kode_tabungan = fields.Char('Kode Tabungan')
    ratetab_ids =fields.One2many(comodel_name='yudha.rate.tabungan',inverse_name='tab_id',string='Tabungan Rates')
    state = fields.Boolean(string='Active')

    def toggle_active(self):
        self.state = True

    def tampil_rate(self):
        tab_id = self.id
        rel_view_id = self.env.ref('yudha_simpan_pinjam.rate_tabungan_tree_view')
        if not tab_id:
            raise Warning("No Tabungan not found.!")
        else:
            return {
                'domain': [('tab_id', '=', tab_id)],
                'view_mode': 'tree,form',
                'views': [(rel_view_id.id, 'tree')],
                'name': 'Rate Tabungan',
                'res_model': 'yudha.rate.tabungan',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

