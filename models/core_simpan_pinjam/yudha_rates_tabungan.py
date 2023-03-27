# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

class yudha_rate_tabungan(models.Model):
    _name = 'yudha.rate.tabungan'
    _order = 'docnum desc'
    _description = "yudha RATES TABUNGAN"

    tgl_input = fields.Date(string='Tanggal', required=True, default=lambda self: time.strftime("%Y-%m-%d"),
                              help='Tanggal', store=True)
    rate_tab = fields.Float('Rates', digits=(19, 2))
    comp_id = fields.Many2one(comodel_name='res.company',inverse_name='id',string='Company')
    bunga_tab = fields.Integer('Bunga dibayarkan %', default=0, required=True)
    tab_id = fields.Many2one(comodel_name='yudha.master.jenis.tabungan',inverse_name='id',string='Jenis Tabungan')


    @api.model
    def default_get(self, fields):
        tab_id = self._context.get('tab_ids')
        rec = super(yudha_rate_tabungan, self).default_get(fields)
        if tab_id:
            rec.update({'tab_id': tab_id[0]})

        return rec


