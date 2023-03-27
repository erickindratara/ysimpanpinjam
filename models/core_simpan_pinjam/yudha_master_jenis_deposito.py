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

class yudha_master_jenis_deposito(models.Model):
    _name = 'yudha.master.jenis.deposito'

    name = fields.Char(string='Jenis Deposito',copy=True, required=True, index=True )
    akun_coa = fields.Many2one('account.account', string='No COA', required=True,index=True)
    jangka_waktu = fields.Integer(string='Jangka Waktu (bln)', required=True)
    ratedepo_ids = fields.One2many(comodel_name='yudha.rate.deposito', inverse_name='depo_id', string='Tabungan Rates')
    state = fields.Boolean(string='Active')

    def toggle_active(self):
        self.state = True

    def tampil_rate(self):
        depo_id=self.id
        rel_view_id = self.env.ref('yudha_simpan_pinjam.rate_deposito_tree_view')
        if not depo_id:
            raise Warning("No Deposito not found.!")
        else:
            return {
                'domain': [('depo_id', '=', depo_id)],
                'view_mode': 'tree,form',
                'views': [(rel_view_id.id, 'tree')],
                'name': 'Rate Deposito',
                'res_model': 'yudha.rate.deposito',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }