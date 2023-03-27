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
import calendar
from datetime import timedelta
from datetime import datetime

SESSION_STATES = [
        ('draft', 'Draft'),
        ('valid', 'Validate'),
        ('paid', 'Paid'),
        ('done', 'Done')
]

class yudha_peminjaman_barang(models.Model):
    _name = 'yudha.peminjaman.barang'
    _order = 'docnum desc'
    _description = "yudha PINJAMAN BARANG"

    docnum = fields.Char(size=100, string='No. Transaksi' , readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Peminjaman barang', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    keterangan = fields.Char(size=100, string='Keterangan')
    jns_trans = fields.Selection([('TD', 'Peminjaman barang'), ('SD', 'Pembayaran Cicilan')], string='Jenis Transaksi',default='TD', help='Jenis Transaksi')
    no_accmove = fields.Many2one('account.move',string='No Journal')
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True,index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jml_pinjam = fields.Float('Jumlah Pinjaman', digits=(19, 2), default=0,required=True)
    no_rek = fields.Char(size=100, string='Nomer Rekening')
    dok_pend = fields.Many2many('ir.attachment',string='Dokument Pendukung')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    #Add by Agus
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    date_start = fields.Date(string='Tanggal Pencairan', required=False,default=lambda self: time.strftime("%Y-%m-%d"))
    date_end = fields.Date(string='Tanggal Akhir Pinjaman', readonly=True, default=lambda self: time.strftime("%Y-%m-%d"))
    lama_cicilan = fields.Integer('Jangka Waktu (bln)', default=1)
    bunga = fields.Float('Suku Bunga pa (%)', digits=(16, 2), readonly=True, store=True, default=0)
    type_bunga = fields.Selection([('tunggal','Efektif Tunggal'),('efektif','Efektif Anuitas'),('tetap','Tetap'),('syariah','Syariah'),('kpr','KPR')], string='Perhitungan Bunga', default='tetap',store=True,readonly=True)
    jml_cicilan_view = fields.Float('Jumlah Angsuran', digits=(16, 2), readonly=True, store=True, default=0)
    jml_cicilan = fields.Float('Jumlah Angsuran', digits=(16, 2), store=True, default=0)
    last_paydate = fields.Date(string='Tgl Angsuran Terakhir', readonly=True, default=lambda self: time.strftime("%Y-%m-%d"))
    jml_bayar = fields.Float('Jumlah Dibayar', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_loan = fields.Float('Sisa Pinjaman', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_cicilan = fields.Integer('Sisa Angsuran', readonly=True, store=True, default=1)
    date_pelunasan = fields.Date(string='Tanggal Pelunasan', default=lambda self: time.strftime("%Y-%m-%d"))
    jml_pelunasan = fields.Float('Jumlah Pelunasan', digits=(16, 2), store=True, default=0)
    ket_lunas = fields.Char(size=200, string='Keterangan Pelunasan')
    pay_ids = fields.One2many(comodel_name="yudha.peminjaman.barang.details",inverse_name="loan_id",
                              string="Detail Pinjaman", required=False, )

    
    def name_get(self):
        result = []
        for s in self:
            name = str(s.docnum)
            result.append((s.id, name))
        return result

    
    def unlink(self):
        for line in self:
                if line.state != 'draft':
                    raise ValidationError(_('Status bukan Draft, tidak bisa dihapus'))
        return super(yudha_peminjaman_barang, self).unlink()

    @api.model
    def create(self, vals):
        if vals['jml_pinjam'] <= 0:
            raise UserError('Jumlah Pinjaman tidak boleh 0 atau negatif')
        if vals['lama_cicilan'] <= 0:
            raise UserError('Lama Cicilan tidak boleh 0 atau negatif')
        rencana_cicilan=0
        for cek in vals['pay_ids']:
            rencana_cicilan += cek[2]['rencana_cicilan']
        if rencana_cicilan < 0:
            raise UserError('Total Cicilan tidak boleh kurang Jumlah Pinjaman')

        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_trans', False):
            dtim = vals['tgl_trans']
        else:
            dtim = self.tgl_trans
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_peminjaman_barang;"""
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
            vals['docnum'] = 'SIMbarang/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMbarang/'+ str(tahun2) + '/' + '1'
        vals['state'] = 'draft'
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
            vals['no_rek '] = my_agt.no_rek_agt

        today = vals['date_start']
        DATE_FORMAT = "%Y-%m-%d"
        from_dt = datetime.strptime(today, DATE_FORMAT)
        date_after_month = from_dt + relativedelta(months=vals['lama_cicilan'])
        #vals['jml_cicilan'] = vals['jml_pinjam'] / vals['lama_cicilan']
        # vals['jml_cicilan_view']=vals['jml_cicilan']
        vals['sisa_cicilan'] = vals['lama_cicilan']
        vals['sisa_loan'] = vals['jml_pinjam']
        vals['date_end'] = date_after_month
        return super(yudha_peminjaman_barang, self).create(vals)


    
    def write(self, vals):
        if self.state=='draft':
            if vals.get('pay_ids', False):
                nilai_rubah = 0
                ch_line=0
                rencana_awal=self.get_rencana_cicilan()
                for cek in vals['pay_ids']:
                    if cek[2] != False:
                        nilai_awal = self.get_value_asal(ch_line)
                        nilai_baru = cek[2]['rencana_cicilan']
                        nilai_rubah += nilai_awal-nilai_baru
                    ch_line += 1

                if rencana_awal-nilai_rubah < 0:
                    raise UserError('Total Cicilan tidak boleh kurang Jumlah Pinjaman')


            if vals.get('partner_id.name', False):
                nm_agt = vals['partner_id.name']
            else:
                nm_agt = self.partner_id.name
            my_agt = self.env['res.partner'].search([('name', '=', nm_agt)])
            if my_agt:
                vals['no_agt'] = my_agt.no_anggota
                vals['npk'] = my_agt.npk
                vals['unit_kerja'] = my_agt.unit_kerja
                vals['no_rek'] = my_agt.no_rek_agt

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
            vals['jml_cicilan_view'] = jml_cicilan

            if lama_cicilan !=0:
                #vals['jml_cicilan'] = jml_pinjam / lama_cicilan
                vals['sisa_loan'] = jml_pinjam - jml_bayar
                #vals['sisa_cicilan'] = vals['sisa_loan']/jml_cicilan
                today = self.date_start
                DATE_FORMAT = "%Y-%m-%d"
                from_dt = datetime.strptime(today, DATE_FORMAT)
                date_after_month = from_dt + relativedelta(months=lama_cicilan)
                vals['date_end'] = date_after_month

        return super(yudha_peminjaman_barang, self).write(vals)

    def get_value_asal(self,ch_line):
        line=0
        for cek in self.pay_ids:
            if line==ch_line:
                return cek['rencana_cicilan']
            line += 1

    def get_rencana_cicilan(self):
        cicilan_awal=0
        for cek in self.pay_ids:
            cicilan_awal += cek['rencana_cicilan']
        return cicilan_awal


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja
            self.no_rek = my_agt.no_rek_agt

    @api.onchange('lama_cicilan', 'jml_pinjam','bunga','type_bunga', 'date_start')
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
        if self.jml_pinjam>0:
            if self.bunga>0:
                if self.lama_cicilan>0:
                    self.pay_ids = self.get_detail(float(self.jml_pinjam),int(self.lama_cicilan),float(self.bunga)/12/100,self.type_bunga)

    def get_detail(self,P,t,i,type_bunga):
        jml_pinjam=P
        res=[]
        add_line = {'loan_id': self.id,
            'date_pay': self.tgl_trans,
            'description': 'Pinjaman barang',
            'type_pelunasan': 'transfer',
            'rencana_cicilan': jml_pinjam*-1,
            'saldo_pinjaman': jml_pinjam,
            'doc_type': 'outbound',
        }
        res += [add_line]

        if type_bunga == 'efektif':
            DATETIME_FORMAT = "%Y-%m-%d"
            date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
            currentDate = int(date_pay.strftime("%-d"))

            # Angsuran perbulan = P x i / [1-(1+i)^-t]
            jml_cicilan = P * i / (1 - (1 + i) ** -t)
            self.jml_cicilan=round(jml_cicilan)
            self.jml_cicilan_view=round(jml_cicilan)
            for angs in range(1, t+1):
                # Bunga = P * i
                bunga=P * i
                pokok=jml_cicilan-bunga
                P=P-pokok
                #date_pay = self.add_one_month(date_pay)

                date_pay = date_pay + relativedelta(months=1)
                payDate = int(date_pay.strftime("%-d"))
                if payDate-currentDate<0:
                    # cari tanggal terakhir dalam bulan payment
                    year=int(date_pay.strftime("%-Y"))
                    month=int(date_pay.strftime("%-m"))
                    lastdate=calendar.monthrange(year, month)[1]
                    if lastdate-currentDate<0:
                        date_pay= date_pay.replace(day=lastdate)
                    else:
                        date_pay = date_pay.replace(day=currentDate)
                add_line = {'loan_id': self.id,
                            'cicilan_ke': angs,
                            'date_pay': date_pay,
                            'description': 'Angsuran ke-'+str(angs),
                            'type_pelunasan': 'gaji',
                            'jml_pokok': round(pokok),
                            'jml_bunga': round(bunga),
                            'rencana_cicilan': round(jml_cicilan),
                            'saldo_pinjaman': round(P),
                            'doc_type': 'inbound',
                            }
                res += [add_line]
        elif type_bunga == 'tetap':
            DATETIME_FORMAT = "%Y-%m-%d"
            date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
            currentDate = int(date_pay.strftime("-%d"))

            # Angsuran perbulan = P / t
            pokok = P/t
            bunga = P * i
            jml_cicilan = pokok + bunga
            self.jml_cicilan=round(jml_cicilan)
            self.jml_cicilan_view=round(jml_cicilan)

            for angs in range(1, t+1):
                #date_pay = self.add_one_month(date_pay)
                P = P-pokok

                date_pay = date_pay + relativedelta(months=1)
                payDate = int(date_pay.strftime("-%d"))
                if payDate-currentDate<0:
                    # cari tanggal terakhir dalam bulan payment
                    year=int(date_pay.strftime("-%Y"))
                    month=int(date_pay.strftime("-%m"))
                    lastdate=calendar.monthrange(year, month)[1]
                    if lastdate-currentDate<0:
                        date_pay= date_pay.replace(day=lastdate)
                    else:
                        date_pay = date_pay.replace(day=currentDate)
                add_line = {'loan_id': self.id,
                            'cicilan_ke': angs,
                            'date_pay': date_pay,
                            'description': 'Angsuran ke-'+str(angs),
                            'type_pelunasan': 'gaji',
                            'jml_pokok': round(pokok),
                            'jml_bunga': round(bunga),
                            'rencana_cicilan': round(jml_cicilan),
                            'saldo_pinjaman': round(P),
                            'doc_type': 'inbound',
                            }
                res += [add_line]
        return res

    def add_months(self,sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        date_pay=datetime.date(year, month, day)
        return date_pay


    def add_one_month(self,t):
        one_day = timedelta(days=1)
        one_month_later = t + one_day
        while one_month_later.month == t.month:  # advance to start of next month
            one_month_later += one_day
        target_month = one_month_later.month
        while one_month_later.day < t.day:  # advance to appropriate day
            one_month_later += one_day
            if one_month_later.month != target_month:  # gone too far
                one_month_later -= one_day
                break
        return one_month_later

class yudha_peminjaman_barang_details(models.Model):
    _name = 'yudha.peminjaman.barang.details'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.barang", inverse_name='id', string="Loan Id", required=False, default=False)
    cicilan_ke = fields.Integer(string='Angs.Ke')
    date_pay = fields.Date(string='Tanggal Angsuran', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    description = fields.Char('Description', size=200, default='')
    jml_pokok = fields.Float('Jumlah Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga = fields.Float('Jumlah Bunga', digits=(16, 2), store=True, default=0)
    rencana_cicilan = fields.Float('Rencana Angsuran', digits=(16, 2), store=True, default=0)
    jml_cicilan = fields.Float('Actual Angsuran', digits=(16, 2), store=True, default=0)
    saldo_pinjaman = fields.Float('Saldo Pinjaman', digits=(16, 2), store=True, default=0)
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')],string='Type')
    type_pelunasan = fields.Selection([('cash', 'Cash'),('transfer', 'Transfer'), ('gaji', 'Potong Gaji')], string='Type Pelunasan',default='cash')
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    valid_bulanan = fields.Many2one(comodel_name="yudha.validasi.bulanan", string="Valid Bulanan Id", required=False, )
    move_id = fields.Many2one('account.move', 'Accounting Entry', copy=False)
    payment_id = fields.Many2one('account.payment', 'Payment Entry', copy=False)
    state = fields.Selection(string="State", selection=([('draft','Draft'),('valid','Validate'),('paid','Paid')]), default='draft')
