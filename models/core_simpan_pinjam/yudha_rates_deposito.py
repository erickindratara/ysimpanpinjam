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

class yudha_rate_deposito(models.Model):
    _name = 'yudha.rate.deposito'
    _order = 'docnum desc'
    _description = "yudha RATES DEPOSITO"

    tgl_input = fields.Date(string='Tanggal', required=True, default=lambda self: time.strftime("%Y-%m-%d"),
                              help='Tanggal', store=True)
    rate_depo = fields.Float('Rates', digits=(19, 2))
    comp_id = fields.Many2one(comodel_name='res.company',inverse_name='id',string='Company')
    bunga_depo = fields.Integer('Bunga dibayarkan %', default=0, required=True)
    depo_id = fields.Many2one(comodel_name='yudha.master.jenis.deposito',inverse_name='id',string='Jenis Simpanan Berjangka')

    @api.model
    def default_get(self, fields):
        depo_id = self._context.get('depo_ids')
        rec = super(yudha_rate_deposito, self).default_get(fields)
        if depo_id:
            rec.update({'depo_id': depo_id[0]})

        return rec
