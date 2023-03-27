# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError

class yudha_res_partner(models.Model):
    _inherit = 'res.partner'

   # category_id = fields.One2many(comodel_name='res.partner.category',inverse_name='id',string='Jenis Kontak', store=True)
    category_id = fields.Selection([('Anggota', 'ANGGOTA'), ('Non Anggota', 'NON ANGGOTA')], string='Jenis Kontak',help='Jenis Kontak')
    #phone = fields.Char(size=100, string='No.Telephone')
    mobile = fields.Char(size=100, string='No. Handphone')
    alamat = fields.Char(size=100, string='Alamat Tempat Tinggal')
    email = fields.Char(size=100, string='Email')
    #alamat_ktp = fields.Char(size=100, string='Alamat sesuai KTP')
    #npwp = fields.Char(size=100, string='NPWP')
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    #no_tel = fields.Char(size=100, string='No. Telepon')
    #no_hp = fields.Char(size=100, string='No. Handphone')
    #email = fields.Char(size=100, string='Email')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan",inverse_name='id', string="Asal Perusahaan")
    jk = fields.Selection([('L', 'Laki-laki'), ('P', 'Perempuan')], string='Jenis Kelamin',help='Jenis Kelamin')
    tgl_gabung = fields.Date(string='Tanggal Bergabung', help='Tanggal Bergabung',store=True)

    nm_bank = fields.Char(size=100, string='Nama Bank')
    no_rek_agt = fields.Char(size=100, string='No Rekening')
    atas_nama = fields.Char(size=100, string='Atas Nama')
    #iuran_pokok_per_bulan = fields.Float('Iuran Pokok Per Bulan', digits=(19, 2), default=0)
    #iuran_wajib_per_bulan = fields.Float('Iuran Wajib Per Bulan', digits=(19, 2), default=0)
    #tipe_anggota = fields.sel
    #Saldo Pinjaman
    iuran_pokok = fields.Float('Saldo Simpanan Pokok', digits=(19, 2), default=0, readonly=True )
    iuran_wajib = fields.Float('Saldo Simpanan Wajib', digits=(19, 2), default=0, readonly=True )
    iuran_sukarela = fields.Float('Saldo Simpanan Sukarela', digits=(19, 2), default=0, readonly=True )
    saldo_tab_agt = fields.Float('Saldo Tabungan Anggota', digits=(19, 2), default=0, readonly=True )
    tab_agt_bln = fields.Float('Tabungan Anggota Bulanan', digits=(19, 2), default=0, readonly=True)
    saldo_masyarakat_bln = fields.Float('Saldo Tabungan Masyarakat', digits=(19, 2), default=0, readonly=True)
    tab_masyarakat_bln = fields.Float('Tabungan Masyarakat Bulanan', digits=(19, 2), default=0, readonly=True)
    saldo_tab_khusus = fields.Float('Saldo Tabungan Khusus', digits=(19, 2), default=0, readonly=True)
    tab_khusus_bln = fields.Float('Tabungan Khusus Bulanan', digits=(19, 2), default=0, readonly=True)
    saldo_deposito = fields.Float('Saldo Simpanan Berjangka', digits=(19, 2), default=0, readonly=True )
    pinj_dana = fields.Float('Saldo Pinjaman Dana', digits=(19, 2), default=0, readonly=True )
    pinj_konsumtif = fields.Float('Saldo Pinjaman Konsumtif', digits=(19, 2), default=0, readonly=True )
    pinj_syariah = fields.Float('Saldo Pinjaman Syariah', digits=(19, 2), default=0, readonly=True)
    pinj_barang = fields.Float('Saldo Pinjaman Barang', digits=(19, 2), default=0, readonly=True)
    pinj_sembako = fields.Float('Saldo Pinjaman Sembako', digits=(19, 2), default=0, readonly=True)
    pot_tab = fields.Float('Potongan Tabungan', digits=(19, 2), default=0, readonly=False)

    @api.model
    def create(self, vals):
        if vals.get('category_id', False):
            #cat_name = self.TagsName(vals['category_id'])
            cat_name = vals['category_id']
        else:
            cat_name = self.category_id
        if vals.get('asal_pt', False):
            ptasal = vals['asal_pt']
        else:
            ptasal = self.asal_pt
        if vals.get('jk', False):
            myjk = vals['jk']
        else:
            myjk = self.jk
        if vals.get('tgl_gabung',False):
            tglgab = vals['tgl_gabung']
        else:
            tglgab = self.tgl_gabung

        if vals.get('no_anggota', False):
            noagt = vals['no_anggota']
        else:
            noagt = self.no_anggota

        if cat_name =='Anggota':
            if noagt == False:
                raise UserError((
                                    'Contact Error,!\n'
                                    'Field  Nomer Anggota tidak boleh kosong '))

        return super(yudha_res_partner, self).create(vals)

    def write(self, vals):
        if vals.get('category_id', False):
            #cat_name = self.TagsName(vals['category_id'])
            cat_name = vals['category_id']
        else:
            cat_name = self.category_id

        if vals.get('asal_pt', False):
            ptasal = vals['asal_pt']
        else:
            ptasal = self.asal_pt

        if vals.get('jk', False):
            myjk = vals['jk']
        else:
            myjk = self.jk

        if vals.get('tgl_gabung',False):
            tglgab = vals['tgl_gabung']
        else:
            tglgab = self.tgl_gabung

        if vals.get('no_anggota', False):
            noagt = vals['no_anggota']
        else:
            noagt = self.no_anggota

        if cat_name =='Anggota':
            if noagt == False:
                raise UserError((
                                    'Contact Error,!\n'
                                    'Field  Nomer Anggota tidak boleh kosong '))

        return super(yudha_res_partner, self).write(vals)
