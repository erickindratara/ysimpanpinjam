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

class yudha_peminjaman_syariah(models.Model):
    _name = 'yudha.peminjaman.syariah'
    _order = 'docnum desc'
    _description = "yudha PINJAMAN SYARIAH"

    docnum = fields.Char(size=100,  string='No. Transaksi' , readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Peminjaman Syariah', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    keterangan = fields.Char(size=100, string='Keterangan')
    jns_trans = fields.Selection([('TD', 'Peminjaman Syariah'), ('SD', 'Pembayaran Cicilan')], string='Jenis Transaksi',default='TD', help='Jenis Transaksi')
    no_accmove = fields.Many2one('account.move',string='No Journal')
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True,index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jml_pinjam = fields.Float('Jumlah Pinjaman', digits=(19, 2), default=0,required=True)
    no_rek = fields.Char(size=100, string='Nomer Rekening')
    dok_pend = fields.Many2many('ir.attachment',
                                string='Dokument Pendukung')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    #Add by Agus
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    date_start = fields.Date(string='Tanggal Pencairan', required=False,default=lambda self: time.strftime("%Y-%m-%d"))
    date_bayar = fields.Integer(string='Tanggal Jatuh Tempo', default=1)
    date_end = fields.Date(string='Tanggal Akhir Pinjaman', readonly=True, default=lambda self: time.strftime("%Y-%m-%d"))
    lama_cicilan = fields.Integer('Jangka Waktu (bln)', default=1)
    bunga = fields.Float('Suku Bunga pa (%)', digits=(16, 2), store=True, default=0)
    pot_thr = fields.Float('Potongan THR', digits=(16, 2), store=True, default=0)
    pot_ik = fields.Float('Potongan IK', digits=(16, 2), store=True, default=0)
    pot_jasop = fields.Float('Potongan JASOP', digits=(16, 2), store=True, default=0)
    type_bunga = fields.Selection([('tunggal','Efektif Tunggal'),('efektif','Efektif Anuitas'),('tetap','Tetap'),('syariah','Syariah/KPR')], string='Perhitungan Bunga', default='syariah',store=True,readonly=True)
    jml_cicilan_view = fields.Float('Jumlah Angsuran', digits=(16, 2), readonly=True, store=True, default=0)
    jml_cicilan = fields.Float('Jumlah Angsuran', digits=(16, 2), store=True, default=0)
    last_paydate = fields.Date(string='Tgl Angsuran Terakhir', readonly=True, default=lambda self: time.strftime("%Y-%m-%d"))
    jml_bayar = fields.Float('Jumlah Dibayar', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_loan = fields.Float('Sisa Pinjaman', digits=(16, 2), readonly=True, store=True, default=0)
    sisa_cicilan = fields.Integer('Sisa Angsuran', readonly=True, store=True, default=1)
    date_pelunasan = fields.Date(string='Tanggal Pelunasan', default=lambda self: time.strftime("%Y-%m-%d"))
    jml_pelunasan = fields.Float('Jumlah Pelunasan', digits=(16, 2), store=True, default=0)
    ket_lunas = fields.Char(size=200, string='Keterangan Pelunasan')
    pay_ids = fields.One2many(comodel_name="yudha.peminjaman.syariah.details",inverse_name="loan_id", string="Detail Pinjaman", required=False, )
    summary_ids = fields.One2many(comodel_name="yudha.peminjaman.syariah.summary",inverse_name="loan_id", string="Summary Angsuran", required=False, )

    
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
        return super(yudha_peminjaman_syariah, self).unlink()

    @api.model
    def create(self, vals):
        if vals['jml_pinjam'] <= 0:
            raise UserError('Jumlah Pinjaman tidak boleh 0 atau negatif')
        if vals['lama_cicilan'] <= 0:
            raise UserError('Lama Cicilan tidak boleh 0 atau negatif')
        # rencana_cicilan=0
        # for cek in vals['pay_ids']:
        #     rencana_cicilan += cek[2]['rencana_cicilan']
        # if rencana_cicilan < 0:
        #     raise UserError('Total Cicilan tidak boleh kurang Jumlah Pinjaman')

        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_trans', False):
            dtim = vals['tgl_trans']
        else:
            dtim = self.tgl_trans
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_peminjaman_syariah;"""
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
            vals['docnum'] = 'SIMsyariah/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMsyariah/'+ str(tahun2) + '/' + '1'
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
        return super(yudha_peminjaman_syariah, self).create(vals)


    
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

                #if rencana_awal-nilai_rubah < 0:
                #    raise UserError('Total Cicilan tidak boleh kurang Jumlah Pinjaman')


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

        return super(yudha_peminjaman_syariah, self).write(vals)

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

    @api.onchange('lama_cicilan', 'jml_pinjam','bunga','type_bunga', 'date_start','date_bayar')
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
                    self.summary_ids = self.get_summary(float(self.jml_pinjam),int(self.lama_cicilan),float(self.bunga)/12/100,self.type_bunga)
                    self.pay_ids = self.get_detail(float(self.jml_pinjam),int(self.lama_cicilan),float(self.bunga)/12/100,self.type_bunga)

    def get_summary(self, P, t, i, type_bunga):
        DATETIME_FORMAT = "%Y-%m-%d"
        date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
        currentDate = int(date_pay.strftime("-%d"))
        i_tahun = self.bunga/100
        t_tahun = int(int(self.lama_cicilan) / 12)
        # Angsuran perbulan = P x i / [1-(1+i)^-t]
        cicilan_pertahun = P * i_tahun / (1 - (1 + i_tahun) ** -t_tahun)
        setting_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
        porsi_gaji = setting_obj.pot_gaji
        porsi_thr = setting_obj.pot_thr
        porsi_ik = setting_obj.pot_ik
        porsi_jasop = setting_obj.pot_jasop

        cicilan_bulanan = cicilan_pertahun * porsi_gaji / 100 / 12
        cicilan_triwulan = cicilan_pertahun * porsi_ik / 100 / 4
        cicilan_thr = cicilan_pertahun * (porsi_thr/ 100)
        cicilan_jasop = cicilan_pertahun * (porsi_jasop/ 100)
        cicilan_tahunan = cicilan_thr + cicilan_jasop

        self.pot_thr=round(cicilan_thr)
        self.pot_ik=round(cicilan_triwulan)
        self.pot_jasop=round(cicilan_jasop)

        pinjaman_total = cicilan_pertahun * t_tahun
        pinjaman_bunga = pinjaman_total - P
        jml_cicilan = cicilan_bulanan
        self.jml_cicilan = round(jml_cicilan)
        self.jml_cicilan_view = round(jml_cicilan)
        res_tahun = []
        add_summary = {}
        add_summary = {'loan_id': self.id,
                       'tahun_ke': 0,
                       'pinjaman_total': round(pinjaman_total),
                       'pinjaman_pokok': round(P),
                       'pinjaman_bunga': round(pinjaman_bunga),
                       }
        res_tahun += [add_summary]
        for angs in range(1, t_tahun+1):
            # Bunga = P * i
            bunga=P * i_tahun
            pokok=cicilan_pertahun-bunga
            P=P-pokok
            pinjaman_total=pinjaman_total-cicilan_pertahun
            pinjaman_bunga=pinjaman_total-P
            add_summary = {'loan_id': self.id,
               'tahun_ke': angs,
               'cicilan_total': round(cicilan_pertahun),
               'cicilan_pokok': round(pokok),
               'cicilan_bunga': round(bunga),
               'pinjaman_total': round(pinjaman_total),
               'pinjaman_pokok': round(P),
               'pinjaman_bunga': round(pinjaman_bunga),
               'cicilan_perbulan': round(cicilan_bulanan),
               'cicilan_pertriwulan': round(cicilan_triwulan),
               'cicilan_tahunan': round(cicilan_tahunan),
               }
            res_tahun += [add_summary]
        return res_tahun



    def get_detail(self,P,t,i,type_bunga):
        jml_pinjam=P
        res=[]
        add_line={}
        add_line = {'loan_id': self.id,
            'date_pay': self.tgl_trans,
            'description': 'Pinjaman Syariah',
            'type_pelunasan': 'transfer',
            'rencana_cicilan': jml_pinjam*-1,
            'rencana_cicilan_report': jml_pinjam*-1,
            'saldo_pinjaman': jml_pinjam,
            'saldo_pinjaman_report': jml_pinjam,
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
            currentDate = int(date_pay.strftime("%-d"))

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
        elif type_bunga == 'tunggal':
            DATETIME_FORMAT = "%Y-%m-%d"
            date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
            currentDate = int(date_pay.strftime("%-d"))
            #menggunakan bunga harian
            i=(i*12)/365
            # Angsuran perbulan = P x i / [1-(1+i)^-t]
            jml_cicilan = P * i / (1 - (1 + i) ** -t)
            self.jml_cicilan=round(jml_cicilan)
            self.jml_cicilan_view=round(jml_cicilan)
            for angs in range(1, t+1):
                # Bunga = P * i
                pokok=0
                P=P-pokok
                #date_pay = self.add_one_month(date_pay)
                if angs==1:
                    selisih_date = self.date_bayar-currentDate
                    if selisih_date<0:
                        # cari tanggal terakhir dalam bulan payment
                        year = int(date_pay.strftime("%-Y"))
                        month = int(date_pay.strftime("%-m"))
                        lastdate = calendar.monthrange(year, month)[1]
                        selisih_date=lastdate-currentDate+self.date_bayar
                    date_pay = date_pay + relativedelta(days=selisih_date)
                    currentDate = int(date_pay.strftime("%-d"))
                else:
                    date_pay2 = date_pay + relativedelta(months=1)
                    #difference = relativedelta(date_pay2, date_pay)
                    delta = date_pay2 - date_pay
                    selisih_date=delta.days
                    date_pay = date_pay + relativedelta(days=selisih_date)
                payDate = int(date_pay.strftime("%-d"))
                if payDate-currentDate<0:
                    # cari tanggal terakhir dalam bulan payment
                    year=int(date_pay.strftime("%-Y"))
                    month=int(date_pay.strftime("%-m"))
                    selisih_date=selisih_date+(payDate-currentDate)
                    lastdate=calendar.monthrange(year, month)[1]
                    if lastdate-currentDate<0:
                        date_pay= date_pay.replace(day=lastdate)
                    else:
                        date_pay = date_pay.replace(day=currentDate)
                bunga = P * i * selisih_date
                jml_cicilan = bunga
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
        elif type_bunga == 'syariah':
            DATETIME_FORMAT = "%Y-%m-%d"
            date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
            currentDate = int(date_pay.strftime("%-d"))
            i_tahun = self.bunga / 100
            t_tahun = int(int(self.lama_cicilan) / 12)
            # Angsuran perbulan = P x i / [1-(1+i)^-t]
            jml_cicilan = P * i / (1 - (1 + i) ** -t)
            P_bln=P
            P_report=P
            hutang_bunga_bln=0
            cicilan_pertahun = P * i_tahun / (1 - (1 + i_tahun) ** -t_tahun)
            setting_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
            porsi_gaji = setting_obj.pot_gaji
            porsi_thr = setting_obj.pot_thr
            porsi_ik = setting_obj.pot_ik
            porsi_jasop = setting_obj.pot_jasop

            cicilan_bulanan = cicilan_pertahun * porsi_gaji / 100 / 12
            cicilan_triwulan = cicilan_pertahun * porsi_ik / 100 / 4
            cicilan_thr = cicilan_pertahun * (porsi_thr / 100)
            cicilan_jasop = cicilan_pertahun * (porsi_jasop / 100)
            cicilan_tahunan = cicilan_thr + cicilan_jasop

            for angs in range(1, t+1):
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
                add_bunga = (angs - 1) % 12
                if add_bunga == 0:
                    if angs == 1:
                        thn = 1
                        date_pay = datetime.strptime(self.date_start, DATETIME_FORMAT)
                    else:
                        thn = int(1+((angs - 1) / 12))

                    for line in self.summary_ids:
                        if line['tahun_ke'] == thn:
                            beban_bunga = line['cicilan_bunga']
                            break
                    P = P + beban_bunga
                    P_report = P_report + beban_bunga
                    add_line = {'loan_id': self.id,
                                'cicilan_ke': angs,
                                'date_pay': date_pay,
                                'description': 'Beban Bunga tahun ke-' + str(thn),
                                'type_pelunasan': 'transfer',
                                'rencana_cicilan': round(beban_bunga * -1),
                                'rencana_cicilan_report': round(beban_bunga * -1),
                                'saldo_pinjaman': round(P),
                                'saldo_pinjaman_report': round(P_report),
                                'doc_type': 'outbound',
                                }
                    res += [add_line]
                    beban_bunga_bln = beban_bunga/12

                currentMonth = int(date_pay.strftime("%-m"))
                triwulan=0
                if currentMonth in (3,6,9,12):
                    triwulan=cicilan_triwulan
                tahunan=0
                if currentMonth == 5:
                    tahunan=cicilan_tahunan

                total_cicilan = cicilan_bulanan

                total_cicilan_report=cicilan_bulanan+triwulan+tahunan
                total_beban_bunga=beban_bunga_bln+hutang_bunga_bln
                if total_cicilan_report<total_beban_bunga:
                    bunga_report=total_cicilan_report
                    pokok_report = 0
                    hutang_bunga_bln+=beban_bunga_bln-total_cicilan_report
                else:
                    bunga_report=total_beban_bunga
                    pokok_report=total_cicilan_report-total_beban_bunga
                    hutang_bunga_bln=0
                P_bln = P_bln - pokok_report
                P_report=P_report-total_cicilan_report

                #P=P-total_cicilan
                #versi lama di hidden dulu
                # add_line = {'loan_id': self.id,
                #             'cicilan_ke': angs,
                #             'date_pay': date_pay,
                #             'description': 'Angsuran ke-'+str(angs),
                #             'type_pelunasan': 'gaji',
                #             'jml_pokok': round(pokok),
                #             'jml_bunga': round(bunga),
                #             'saldo_pinjaman_bln': round(P_bln),
                #             'cicilan_bulanan': round(cicilan_bulanan),
                #             'cicilan_triwulan': round(triwulan),
                #             'cicilan_tahunan': round(tahunan),
                #             'rencana_cicilan': round(total_cicilan),
                #             'saldo_pinjaman': round(P),
                #             'doc_type': 'inbound',
                #             }
                add_line = {'loan_id': self.id,
                            'cicilan_ke': angs,
                            'date_pay': date_pay,
                            'description': 'Angsuran ke-'+str(angs),
                            'type_pelunasan': 'gaji',
                            'jml_pokok': 0,
                            'jml_bunga': 0,
                            'cicilan_bulanan': round(cicilan_bulanan),
                            'cicilan_triwulan': 0,
                            'cicilan_tahunan': 0,
                            'rencana_cicilan': round(total_cicilan),
                            'saldo_pinjaman': round(P),
                            'jml_pokok_report': round(pokok_report),
                            'jml_bunga_report': round(bunga_report),
                            'cicilan_triwulan_report': round(triwulan),
                            'cicilan_tahunan_report': round(tahunan),
                            'rencana_cicilan_report': round(total_cicilan_report),
                            'saldo_pinjaman_bln_report': round(P_bln),
                            'saldo_pinjaman_report': round(P_report),
                            'doc_type': 'inbound',
                            }
                res += [add_line]
        return res

    def monthdelta(self, d1, d2):
        delta = 0
        while True:
            mdays = calendar.monthrange(d1.year, d1.month)[1]
            d1 += timedelta(days=mdays)
            if d1 <= d2:
                delta += 1
            else:
                break
        return delta
    
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

class yudha_peminjaman_syariah_details(models.Model):
    _name = 'yudha.peminjaman.syariah.details'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.syariah", inverse_name='id', string="Loan Id", required=False, default=False)
    cicilan_ke = fields.Integer(string='Angs.Ke')
    date_pay = fields.Date(string='Tanggal Angsuran', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    description = fields.Char('Description', size=200, default='')
    jml_pokok = fields.Float('Jumlah Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga = fields.Float('Jumlah Bunga', digits=(16, 2), store=True, default=0)
    cicilan_bulanan = fields.Float('Angs. Bulanan', digits=(16, 2), store=True, default=0)
    cicilan_triwulan = fields.Float('Angs. Triwulan', digits=(16, 2), store=True, default=0)
    cicilan_tahunan = fields.Float('Angs. Tahunan', digits=(16, 2), store=True, default=0)
    rencana_cicilan = fields.Float('Rencana Angsuran', digits=(16, 2), store=True, default=0)
    jml_cicilan = fields.Float('Actual Angsuran', digits=(16, 2), store=True, default=0)
    saldo_pinjaman = fields.Float('Saldo Pinjaman', digits=(16, 2), store=True, default=0)
    jml_pokok_report = fields.Float('Jumlah Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga_report = fields.Float('Jumlah Bunga', digits=(16, 2), store=True, default=0)
    cicilan_triwulan_report = fields.Float('Angs. Triwulan', digits=(16, 2), store=True, default=0)
    cicilan_tahunan_report = fields.Float('Angs. Tahunan', digits=(16, 2), store=True, default=0)
    rencana_cicilan_report = fields.Float('Rencana Angsuran', digits=(16, 2), store=True, default=0)
    saldo_pinjaman_bln_report = fields.Float('Saldo Pinjaman Bulan', digits=(16, 2), store=True, default=0)
    saldo_pinjaman_report = fields.Float('Saldo Pinjaman', digits=(16, 2), store=True, default=0)
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')],string='Type')
    type_pelunasan = fields.Selection([('cash', 'Cash'),('transfer', 'Transfer'), ('gaji', 'Potong Gaji')], string='Type Pelunasan',default='cash')
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    valid_bulanan = fields.Many2one(comodel_name="yudha.validasi.bulanan", string="Valid Bulanan Id", required=False, )
    move_id = fields.Many2one('account.move', 'Accounting Entry', copy=False)
    payment_id = fields.Many2one('account.payment', 'Payment Entry', copy=False)
    state = fields.Selection(string="State", selection=([('draft','Draft'),('valid','Validate'),('paid','Paid')]), default='draft')


class yudha_peminjaman_syariah_summary(models.Model):
    _name = 'yudha.peminjaman.syariah.summary'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.syariah", inverse_name='id', string="Loan Id", required=False, default=False)
    tahun_ke = fields.Integer(string='Tahun Ke')
    cicilan_total = fields.Float('Angs.Total', digits=(16, 2), store=True, default=0)
    cicilan_pokok = fields.Float('Angs.Pokok', digits=(16, 2), store=True, default=0)
    cicilan_bunga = fields.Float('Angs.Bunga', digits=(16, 2), store=True, default=0)
    pinjaman_total = fields.Float('Pinjaman Total', digits=(16, 2), store=True, default=0)
    pinjaman_pokok = fields.Float('Pinjaman Pokok', digits=(16, 2), store=True, default=0)
    pinjaman_bunga = fields.Float('Pinjaman Bunga', digits=(16, 2), store=True, default=0)
    cicilan_perbulan = fields.Float('Angs. per Bulan', digits=(16, 2), store=True, default=0)
    cicilan_pertriwulan = fields.Float('Angs. per Triwulan', digits=(16, 2), store=True, default=0)
    cicilan_tahunan = fields.Float('Angs. Tahunan', digits=(16, 2), store=True, default=0)
