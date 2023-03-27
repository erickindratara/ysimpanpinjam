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
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
]

class yudha_permintaan_barang(models.Model):
    _name = 'yudha.permintaan.barang'

    nama = fields.Many2one('res.partner', string='Nama', required=True,index=True,domain="[('active', '=', 'Y')]")
    ttl  = fields.Char(size=100, string='Tempat/Tanggal Lahir', required=True)
    no_anggota  = fields.Char(size=100, string='Nomor Anggota', required=True)
    golongan = fields.Char(size=100, string='N P K / Golongan', required=True)
    unit_kerja = fields.Char(size=100, string='Department / Unit Kerja', required=True)
    no_hp = fields.Char(size=100, string='Tempat/Tanggal Lahir', required=True)
    bulan_angsuran = fields.Integer('Bulan Angsuran', required=True)
    bayar_bulan = fields.Float('Pembayaran/Bulan', digits=(19, 2), default=0, required=True)
    nilai_pesanan = fields.Float('Nilai Pesanan', digits=(19, 2), default=0, required=True)
    uang_muka = fields.Float('Uang Muka', digits=(19, 2), default=0, required=True)
    sisa_pinjaman = fields.Float('Sisa Pinjaman', digits=(19, 2), default=0, required=True)
    jasa_koperasi = fields.Float('Jasa Koperasi 13% per Tahun', digits=(19, 2), default=0, required=True)
    yudha_minta_ids = fields.One2many(comodel_name='yudha.permintaan.barang.details',inverse_name="yudha_minta_val",string='Timbang Final BPB')
    tgl_minta = fields.Date(string='Tanggal Permohonan', required=True, default=lambda self: time.strftime("%Y-%m-%d"))
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])


class yudha_permintaan_barang_details(models.Model):
    _name = 'yudha.permintaan.barang.details'

    yudha_minta_val = fields.Many2one(comodel_name='yudha.permintaan.barang', inverse_name='id', string="Tally Combine ID",
                               required=False,store=True,index=True,invisible='false' )
    prod_id = fields.Many2one(comodel_name='product.product', inverse_name='id', string='Nama Barang', default='',
                                 help='Nama Barang', required=True, store=True)
    type = fields.Char(size=100, string='Type', required=True)
    kuantitas = fields.Integer('Kuantitas', required=True)
    keterangan = fields.Char(size=100, string='Keterangan', required=True)
