import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import time

SESSION_STATES = [
    ('active', 'Active'),
    ('in active', 'In Active')
]


class yudha_master_golongan(models.Model):
    _name = 'yudha.master.golongan'

    name = fields.Char(string='Nama Golongan', copy=True, required=True, index=True)
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])