# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
import time
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
import calendar
from datetime import timedelta

SESSION_STATES = [
        ('ready', 'Ready'),
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
        ('paid', 'Paid')
]

#Notes by AK:
# ready : pada saat setoran deposito diinput
# deposit  : pada saat dilakukan validasi harian
# payment : pada saat validasi harian - proses pencairan type Transfer
# paid  : pada saat sudah dilakukan Transfer/penarikan Tunai/pemindahan ke Tabungan

class yudha_deposito(models.Model):
    _name = 'yudha.deposito'
    _order = 'docnum desc'
    _description = "yudha SIMPANAN BERJANGKA"

    docnum = fields.Char(size=100, string='No. Transaksi',readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Simpanan Berjangka', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jatuh_tempo = fields.Date(string='Jatuh Tempo', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    #partner_id = fields.Many2one('res.partner', string='Anggota', required=True, index=True, domain="[('category_id', '=', 'Anggota')]")
    no_accmove = fields.Many2one('account.move', string='No Account Move')
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',default='SD', help='Jenis Transaksi')
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='No. Anggota')
    bunga_depo = fields.Float('Bunga pa (%)', digits=(19, 2), default=0, readonly=True)
    jns_depo = fields.Many2one('yudha.master.jenis.deposito', string='Jenis Deposito', required=True)
    jangka_waktu = fields.Integer(string='Jangka Waktu (bln)', readonly=True)
    bayar_bunga = fields.Selection([('tabungan', 'Tabungan'), ('transfer', 'Transfer')], string='Pembayaran Bunga',help='Pembayaran Bunga')
    no_rekening = fields.Many2one(comodel_name="yudha.register.tabungan", inverse_name='id', string="No. Rekening",required=True, index=True)
    nama_rekening = fields.Char(size=100, string='Atas nama', readonly=True)
    jml_depo = fields.Float('Jumlah Deposito', digits=(19, 2), default=0)
    asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], string='Sumber Dana',help='Sumber Dana')
    no_rek_bank = fields.Many2one('account.journal', string='No Rekening USP', required=False, index=True,
                                  domain="['&',('type', '=', 'bank'),('company_id','=',3)]")
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    atasnama = fields.Char(size=100, string='Atas nama')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    keterangan = fields.Char(size=100, string='Keterangan')
    depo_ids = fields.One2many(comodel_name="yudha.deposito.details", inverse_name="depo_id",
                              string="Detail Deposito", required=False, )
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    
    def name_get(self):
        result = []
        for s in self:
            name = str(s.docnum)
            result.append((s.id, name))
        return result

    @api.model
    def create(self, vals):
        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_trans', False):
            dtim = vals['tgl_trans']
        else:
            dtim = self.tgl_trans
        if vals.get('no_rekening', False):
            no_rekening = vals['no_rekening']
            vals['nama_rekening']= self.env['yudha.register.tabungan'].search([('id', '=', no_rekening)]).atasnama
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_deposito;"""
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
            vals['docnum'] = 'SIMDEPO/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMDEPO/'+ str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        vals['jangka_waktu'] = self.env['yudha.master.jenis.deposito'].search([('id', '=', vals['jns_depo'])]).jangka_waktu
        return super(yudha_deposito, self).create(vals)

    @api.onchange('no_agt','partner_id')
    def domain_rekening(self):
        if not self.no_agt:
            return {'domain': {'no_rekening': [('id', '=', [])]}}
        if not self.partner_id:
            return {'domain': {'no_rekening': [('id', '=', [])]}}
        partner_id = self.env['res.partner'].search([('no_anggota', '=', self.no_agt)])

        sql_query = """select id from yudha_register_tabungan where partner_id=%s
                 """
        self.env.cr.execute(sql_query,(partner_id.id,))
        res_id = self.env.cr.dictfetchall()
        rek_list = []
        if res_id != False:
            for field in res_id:
                rek_list.append(field['id'])
        return {'domain': {'no_rekening': [('id', '=', rek_list)]}}

    @api.onchange('no_rekening')
    def onchange_no_rekening(self):
        if not self.no_rekening:
            return
#        no_rekening = self.env['yudha.register.tabungan'].search([('id', '=', self.no_rekening.id)])
        self.nama_rekening = self.no_rekening.atasnama

    
    def write(self, vals):
        if vals.get('jns_depo', False):
            jns_depo = vals['jns_depo']
        else:
            jns_depo = self.jns_depo.id
        vals['jangka_waktu'] = self.env['yudha.master.jenis.deposito'].search([('id', '=', jns_depo)]).jangka_waktu
        if vals.get('no_rekening', False):
            no_rekening = vals['no_rekening']
            vals['nama_rekening']= self.env['yudha.register.tabungan'].search([('id', '=', no_rekening)]).atasnama

        return super(yudha_deposito, self).write(vals)

    @api.onchange('no_agt')
    def onchange_no_agt(self):
        if not self.no_agt:
            return
        no_agt = self.env['res.partner'].search([('no_anggota', '=', self.no_agt)])
        if no_agt.id != False:
            self.partner_id = no_agt.id
            self.no_rek_agt = no_agt.no_rek_agt
            self.nm_bank = no_agt.nm_bank
            self.atasnama = no_agt.atas_nama

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name','=', self.partner_id.name)])
        if my_agt.id != False:
            self.no_agt = my_agt.no_anggota
            self.no_rek_agt = my_agt.no_rek_agt
            self.nm_bank = my_agt.nm_bank
            self.atasnama = my_agt.atas_nama

    @api.onchange('asal_dana','jns_trans')
    def onchange_asal_dana(self):
        if not self.asal_dana:
            return
        if self.asal_dana =='CS':
            self.no_rek_bank = []
            self.no_rek_agt = ''
            self.atasnama = ''
            self.nm_bank = ''
        else:
            self.no_rek_agt = ''
            self.atasnama = ''
            self.nm_bank = ''

    @api.onchange('jml_depo','jns_depo')
    def onchange_jml_depo(self):
        if not self.jns_depo:
            return
        depo_obj=self.env['yudha.master.jenis.deposito'].search([('id','=',self.jns_depo.id)])
        self.jangka_waktu = depo_obj.jangka_waktu
        rate_obj = self.env['yudha.rate.deposito'].search([('tgl_input', '<=', self.tgl_trans)], order='tgl_input desc', limit=1)
        self.bunga_depo=rate_obj.rate_depo

        if not self.jml_depo:
            return
        self.depo_ids = self.get_detail()

    def get_detail(self):
        date_trans = self.tgl_trans
        jml_depo = self.jml_depo
        bayar_bunga = self.bayar_bunga
        res=[]
        add_line={}
        add_line = {'depo_id': self.id,
            'bulan_ke': 0,
            'date_trans': date_trans,
            'bayar_bunga': bayar_bunga,
            'jml_depo': jml_depo,
            'bunga': 0,
            'pajak': 0,
            'rencana_bayar': 0,
            'jml_actual': jml_depo,
            'description': 'Deposito',
            'state': 'ready',
        }
        res += [add_line]
        rate_depo=self.bunga_depo
        jangka_waktu=self.jangka_waktu
        bunga=jml_depo*rate_depo/100/12
        pajak=bunga*10/100
        rencana_bayar=bunga-pajak
        DATETIME_FORMAT = "%Y-%m-%d"
        date_pay = datetime.strptime(self.tgl_trans, DATETIME_FORMAT)
        currentDate = int(date_pay.strftime("%-d"))

        for bulan in range(1, jangka_waktu + 1):
            date_pay = date_pay + relativedelta(months=1)
            payDate = int(date_pay.strftime("-%d"))
            if payDate - currentDate < 0:
                # cari tanggal terakhir dalam bulan payment
                year = int(date_pay.strftime("-%Y"))
                month = int(date_pay.strftime("-%m"))
                lastdate = calendar.monthrange(year, month)[1]
                if lastdate - currentDate < 0:
                    date_pay = date_pay.replace(day=lastdate)
                else:
                    date_pay = date_pay.replace(day=currentDate)
            add_line = {'depo_id': self.id,
                        'bulan_ke': bulan,
                        'date_trans': date_pay,
                        'bayar_bunga': bayar_bunga,
                        'jml_depo': 0,
                        'jml_bunga': bunga,
                        'jml_pajak': pajak,
                        'rencana_bayar': rencana_bayar,
                        'jml_actual': 0,
                        'description': 'Bunga Deposito',
                        'state': 'ready',
                        }
            res += [add_line]
        return res

class yudha_deposito_details(models.Model):
    _name = 'yudha.deposito.details'

    depo_id = fields.Many2one(comodel_name="yudha.deposito", inverse_name='id', string="Depo Id", required=False, default=False)
    bulan_ke = fields.Integer(string='Bulan Ke')
    date_trans = fields.Date(string='Jatuh Tempo', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jml_depo = fields.Float('Jumlah Deposito', digits=(16, 2), store=True, default=0)
    bayar_bunga = fields.Selection([('tabungan', 'Tabungan'), ('transfer', 'Transfer')], string='Pembayaran Bunga')
    jml_bunga = fields.Float('Bunga', digits=(16, 2), store=True, default=0)
    jml_pajak = fields.Float('Pajak', digits=(16, 2), store=True, default=0)
    rencana_bayar = fields.Float('Rencana Bayar', digits=(16, 2), store=True, default=0)
    jml_actual = fields.Float('Realisasi', digits=(16, 2), store=True, default=0)
    description = fields.Char('Keterangan', size=200, default='')
    valid_harian = fields.Many2one(comodel_name="yudha.validasi.harian", string="Valid Harian Id", required=False, )
    state = fields.Selection(string="State", selection=([('ready', 'Ready'), ('valid', 'Validate'), ('done', 'Done')]),
                             default='ready')

class yudha_deposito_details_transfer(models.Model):
    _name = 'yudha.deposito.details.transfer'

    depo_id = fields.Many2one(comodel_name="yudha.deposito", inverse_name='id', string="Depo Id", required=False, default=False)
    docnum = fields.Char(size=100, string='No. Transaksi', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True, index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='No. Anggota', readonly=True)
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    atasnama = fields.Char(size=100, string='Atas nama')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    bulan_ke = fields.Integer(string='Bulan Ke')
    date_trans = fields.Date(string='Jatuh Tempo', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    bayar_bunga = fields.Selection([('tabungan', 'Tabungan'), ('transfer', 'Transfer')], string='Pembayaran Bunga')
    jml_bunga = fields.Float('Bunga', digits=(16, 2), store=True, default=0)
    jml_pajak = fields.Float('Pajak', digits=(16, 2), store=True, default=0)
    rencana_bayar = fields.Float('Rencana Bayar', digits=(16, 2), store=True, default=0)
