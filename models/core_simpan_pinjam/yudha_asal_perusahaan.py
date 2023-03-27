# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import time


class yudha_asal_perusahaan(models.Model):
    _name = 'yudha.asal.perusahaan'

    name = fields.Char(string='Nama Perusahaan',copy=True, required=True, index=True )
    kode_nasabah = fields.Char(string='Kode Nasabah',copy=True, required=True, index=True )
