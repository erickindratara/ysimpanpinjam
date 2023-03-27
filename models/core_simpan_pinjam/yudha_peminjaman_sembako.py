# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime

SESSION_STATES = [
        ('draft', 'Draft'),
        ('valid', 'Validate'),
        ('paid', 'Paid'),
        ('done', 'Done')
]

class yudha_peminjaman_sembako(models.Model):
    _name = 'yudha.peminjaman.sembako'
    _order = 'docnum desc'
    _description = "yudha PINJAMAN SEMBAKO"

    docnum = fields.Char(size=100, string='No. Transaksi', readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Peminjaman Sembako', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    #partner_id = fields.Many2one('res.partner', string='Anggota', required=True, index=True, domain="[('category_id', '=', 'Anggota')]")
    keterangan = fields.Char(size=100, string='Keterangan')
    jns_trans = fields.Selection([('TD', 'Peminjaman Dana'), ('SD', 'Pembayaran Cicilan')], string='Jenis Transaksi',default='TD', help='Jenis Transaksi')
    no_accmove = fields.Many2one('account.move',string='No Journal')

    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jml_pinjam = fields.Float('Jumlah Pinjaman', digits=(19, 2), default=0, required =True)
    no_rek = fields.Char(size=100, string='Nomer Rekening')
    dok_pend = fields.Many2many('ir.attachment',
                                string='Dokument Pendukung')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    # Add by Agus
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    date_start = fields.Date(string='Tanggal Mulai Bayar', required=False,default=lambda self: time.strftime("%Y-%m-%d"))
    date_end = fields.Date(string='Tanggal Akhir Bayar', readonly=True, default=lambda self: time.strftime("%Y-%m-%d"))
    lama_cicilan = fields.Integer('Lama Cicilan (bln)', default=1)
    jml_cicilan = fields.Float('Jumlah Cicilan', digits=(16, 2), readonly=True, store=True, default=0)
    jml_bayar = fields.Float('Jumlah Dibayar', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_loan = fields.Float('Sisa Pinjaman', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_cicilan = fields.Integer('Sisa Cicilan', readonly=True, store=True, default=1)
    date_pelunasan = fields.Date(string='Tanggal Pelunasan', default=lambda self: time.strftime("%Y-%m-%d"))
    jml_pelunasan = fields.Float('Jumlah Pelunasan', digits=(16, 2), store=True, default=0)
    ket_lunas = fields.Char(size=200, string='Keterangan Pelunasan')
    pay_ids = fields.One2many(comodel_name="yudha.peminjaman.sembako.details", inverse_name="loan_id",
                              string="Detail Pinjaman", required=False, )


    
    def unlink(self):
        for line in self:
                if line.state != 'draft':
                    raise ValidationError(_('Status bukan Draft, tidak bisa dihapus'))
        return super(yudha_peminjaman_sembako, self).unlink()

    @api.model
    def create(self, vals):
        if vals['jml_pinjam'] <= 0:
            raise UserError('Jumlah Pinjaman tidak boleh 0 atau negatif')
        if vals['lama_cicilan'] <= 0:
            raise UserError('Lama Cicilan tidak boleh 0 atau negatif')

        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_trans', False):
            dtim = vals['tgl_trans']
        else:
            dtim = self.tgl_trans
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_peminjaman_sembako;"""
        self.env.cr.execute(myquery, )
        no_urut = self.env.cr.fetchone()[0]
        nomerurut = 1
        if no_urut != None or no_urut != False:
            urutan = 0
            if str(no_urut).find('/') != -1:
                pecah = no_urut.split('/')
                x = 0
                for satu in pecah:
                    if x == 2:
                       urutan = satu
                    else:
                       urutan = 0
                    x += 1
            nomerurut = int(urutan) + 1
            vals['docnum'] = 'SIMSBK/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMSBK/'+ str(tahun2) + '/' + nomerurut
        vals['state'] = 'draft'
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        print('line 85', nm_agt)
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        today = vals['date_start']
        DATE_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(today, DATE_FORMAT)
        date_after_month = from_dt + relativedelta(months=vals['lama_cicilan'])
        vals['jml_cicilan'] = vals['jml_pinjam'] / vals['lama_cicilan']
        vals['sisa_cicilan'] = vals['lama_cicilan']
        vals['sisa_loan'] = vals['jml_pinjam']
        vals['date_end'] = date_after_month

        return super(yudha_peminjaman_sembako, self).create(vals)

    
    def write(self, vals):
        if vals.get('partner_id.name', False):
            nm_agt = vals['partner_id.name']
        else:
            nm_agt = self.partner_id.name
        my_agt = self.env['res.partner'].search([('name', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja

        if vals.get('date_start'):
            df = vals['date_start']
        else:
            df = self.date_start

        if vals.get('date_end'):
            dt = vals['date_end']
        else:
            dt = self.date_end

        if vals.get('jml_pinjam'):
            jml_pinjam = vals['jml_pinjam']
        else:
            jml_pinjam = self.jml_pinjam

        if vals.get('lama_cicilan'):
            lama_cicilan = vals['lama_cicilan']
        else:
            lama_cicilan = self.lama_cicilan

        if vals.get('jml_bayar'):
            jml_bayar = vals['jml_bayar']
        else:
            jml_bayar = self.jml_bayar

        if vals.get('jml_cicilan'):
            jml_cicilan = vals['jml_cicilan']
        else:
            jml_cicilan = self.jml_cicilan

        if lama_cicilan !=0:
            vals['jml_cicilan'] = jml_pinjam / lama_cicilan
            vals['sisa_loan'] = jml_pinjam - jml_bayar
            vals['sisa_cicilan'] = vals['sisa_loan']/vals['jml_cicilan']
            today = self.date_start
            DATE_FORMAT = "%Y-%m-%d"
            from_dt = datetime.strptime(today, DATE_FORMAT)
            date_after_month = from_dt + relativedelta(months=self.lama_cicilan)
            vals['date_end'] = date_after_month

        return super(yudha_peminjaman_sembako, self).write(vals)


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name','=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja

    @api.onchange('lama_cicilan', 'jml_pinjam', 'date_start')
    def onchange_lama_cicilan(self):
        if not self.partner_id:
            return {'domain': {'partner_id': []}}
        if self.lama_cicilan <= 0:
            raise UserError('Lama Cicilan tidak boleh 0 atau negatif')

        self.jml_cicilan = self.jml_pinjam / self.lama_cicilan
        self.sisa_cicilan = self.lama_cicilan
        self.sisa_loan = self.jml_pinjam - self.jml_bayar

        today = self.date_start
        DATE_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(today, DATE_FORMAT)
        date_after_month = from_dt + relativedelta(months=self.lama_cicilan)
        self.date_end = date_after_month
        self.pay_ids = self.get_detail(float(self.jml_pinjam))

    def get_detail(self,jml_pinjam):
        res=[]
        add_line = {'loan_id': self._origin.id,
            'date_pay': self.tgl_trans,
            'description': 'Pinjaman Dana',
            'type_pelunasan': 'cash',
            'jml_cicilan': jml_pinjam*-1,
            'doc_type': 'outbound',
        }
        res += [add_line]
        return res


class yudha_peminjaman_sembako_details(models.Model):
    _name = 'yudha.peminjaman.sembako.details'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.sembako", inverse_name='id', string="Loan Id", required=False, default=False)
    date_pay = fields.Date(string='Tanggal Bayar', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    description = fields.Char('Description', size=200, default='')
    cicilan_ke = fields.Float('Cicilan Ke', digits=(16, 2), readonly=True, store=True, default=0)
    jml_cicilan = fields.Float('Jumlah', digits=(16, 2), store=True, default=0)
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')],string='Type')
    type_pelunasan = fields.Selection([('cash', 'Cash'), ('gaji', 'Potong Gaji')], string='Type Pelunasan',default='cash')
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    valid_bulanan = fields.Many2one(comodel_name="yudha.validasi.bulanan", string="Valid Bulanan Id", required=False, )
    move_id = fields.Many2one('account.move', 'Accounting Entry', copy=False)
    payment_id = fields.Many2one('account.payment', 'Payment Entry', copy=False)
