# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import datetime


SESSION_STATES = [
        ('ready', 'Ready'),
        ('done', 'Done')
]

class yudha_tabungan(models.Model):
    _name = 'yudha.tabungan'
    _order = 'docnum desc'
    _description = "yudha TABUNGAN"

    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Tabungan', readonly=True)
    docnum = fields.Char(size=100, string='No. Transaksi',readonly=True, index = True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi', default='SD', help='Jenis Transaksi')
    keterangan = fields.Char(size=100, string='Keterangan')
    no_accmove = fields.Many2one('account.move',string='No Account Move')
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True,index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='No. Anggota')
    jenis_tabungan = fields.Many2one(comodel_name="yudha.master.jenis.tabungan",inverse_name='id', string="Jenis Tabungan", required=True, index=True)
    no_rekening = fields.Many2one(comodel_name="yudha.register.tabungan",inverse_name='id', string="No. Rekening", required=True, index=True)
    nama_rekening = fields.Char(size=100, string='Atas nama', readonly=True)
    jml_tab = fields.Float('Jumlah Uang', digits=(19, 2), default=0)
    balance_awal_view = fields.Float('Saldo Awal', digits=(19, 2), default=0, readonly=True)
    balance_awal = fields.Float('Saldo Awal', digits=(19, 2), default=0)
    debit = fields.Float('Jumlah Tarikan', digits=(19, 2), default=0)
    credit = fields.Float('Jumlah Setoran', digits=(19, 2), default=0)
    balance_akhir_view = fields.Float('Saldo Akhir', digits=(19, 2), default=0,readonly=True)
    balance_akhir = fields.Float('Saldo Akhir', digits=(19, 2), default=0)
    asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], string='Sumber Dana',
                                 help='Sumber Dana')
    code_trans = fields.Selection(
        [('STN', 'Setor Tunai'), ('TTN', 'Tarik Tunai'), ('BNT', 'Bunga Tabungan'), ('BND', 'Bunga Deposito'),
         ('PJK', 'Pajak'), ('ADM', 'Biaya Admin')], string='Kode Transaksi')
    no_rek_bank = fields.Many2one('account.journal', string='No Rekening USP', required=False, index=True,
                                  domain="['&',('type', '=', 'bank'),('company_id','=',3)]")
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    atasnama = fields.Char(size=100, string='Atas nama')
    nm_bank = fields.Char(size=100, string='Nama Bank')
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

    @api.onchange('no_agt')
    def onchange_no_anggota(self):
        if not self.no_agt:
            return
        partner_id = self.env['res.partner'].search([('no_anggota', '=', self.no_agt)])
        if partner_id.id != False:
            self.partner_id = partner_id.id
            self.no_rek_agt = partner_id.no_rek_agt
            self.nm_bank = partner_id.nm_bank
            self.atasnama = partner_id.atas_nama

    @api.onchange('partner_id')
    def onchange_no_anggota2(self):
        if not self.partner_id:
            return
        partner_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        if partner_id.id != False:
            self.no_agt = partner_id.no_anggota
            self.no_rek_agt = partner_id.no_rek_agt
            self.nm_bank = partner_id.nm_bank
            self.atasnama = partner_id.atas_nama

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

    
    def unlink(self):
        for line in self:
                if line.state == 'done':
                    raise ValidationError(_('Status Done tidak bisa dihapus'))
        return super(yudha_tabungan, self).unlink()

    @api.model
    def create(self, vals):
        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_trans', False):
            dtim = vals['tgl_trans']
        else:
            dtim = self.tgl_trans
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        vals['balance_awal_view']=vals['balance_awal']
        vals['balance_akhir_view']=vals['balance_akhir']

        vals['nama_rekening']=self.env['yudha.register.tabungan'].search([('id','=',vals['no_rekening'])]).atasnama
        myquery = """SELECT max(docnum) FROM yudha_tabungan;"""
        self.env.cr.execute(myquery,)
        no_urut = self.env.cr.fetchone()[0]
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
            vals['docnum'] = 'SIMTAB/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMTAB/'+ str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        return super(yudha_tabungan, self).create(vals)


    
    def write(self, vals):
        if vals.get('balance_awal', False):
            balance_awal = vals['balance_awal']
        else:
            balance_awal = self.balance_awal
        if vals.get('balance_akhir', False):
            balance_akhir = vals['balance_akhir']
        else:
            balance_akhir = self.balance_akhir

        vals['balance_awal_view']=balance_awal
        vals['balance_akhir_view']=balance_akhir

        return super(yudha_tabungan, self).write(vals)

    @api.onchange('no_agt','partner_id','jenis_tabungan','no_rekening')
    def onchange_no_agt(self):
        if not self.no_agt:
            return
        if not self.jenis_tabungan:
            return
        if not self.no_rekening:
            return
        if not self.partner_id:
            return

        partner_id = self.env['res.partner'].search([('no_anggota', '=', self.no_agt)])
        if partner_id.id != False:
            sql_query = """
                select sum(credit-debit) from yudha_tabungan where state in ('ready','done') and no_rekening=%s and partner_id=%s
                and jenis_tabungan=%s
                """
            self.env.cr.execute(sql_query, (self.no_rekening.id,partner_id.id,self.jenis_tabungan.id,))
            balance_awal = self.env.cr.fetchone()[0] or 0.0
            self.balance_awal_view = balance_awal
            self.balance_awal = balance_awal


    # @api.onchange('partner_id','jenis_tabungan')
    # def onchange_partner_id(self):
    #     if not self.partner_id:
    #         return
    #     if not self.jenis_tabungan:
    #         return
    #     if not self.no_rekening:
    #         return
    #     sql_query = """
    #         select sum(credit-debit) from yudha_tabungan where state in ('ready','done') and no_rekening=%s and partner_id=%s
    #         and jenis_tabungan=%s
    #         """
    #     self.env.cr.execute(sql_query, (self.partner_id.id,self.no_rekening.id,self.jenis_tabungan.id,))
    #     balance_awal = self.env.cr.fetchone()[0] or 0.0
    #     self.balance_awal_view = balance_awal
    #     self.balance_awal = balance_awal




    @api.onchange('asal_dana')
    def onchange_asal_dana(self):
        if not self.asal_dana:
            return
        if self.asal_dana =='CS':
            self.no_rek_bank = []
            self.no_rek_agt = ''
            self.atasnama = ''
            self.nm_bank = ''

    @api.onchange('jns_trans','jml_tab')
    def onchange_jns_trans(self):
        if not self.jns_trans:
            return
        if self.jns_trans=='SD':
            self.credit=self.jml_tab
            self.debit=0
            self.balance_akhir_view=self.balance_awal+self.jml_tab
            self.balance_akhir=self.balance_awal+self.jml_tab
            self.code_trans='STN'
        elif self.jns_trans=='TD':
            self.credit = 0
            balance_akhir = self.balance_awal - self.jml_tab
            if balance_akhir < 0:
                self.debit = 0
                raise ValidationError(_('Saldo tidak mencukupi'))
            self.credit=0
            self.debit=self.jml_tab
            self.balance_akhir_view=self.balance_awal-self.jml_tab
            self.balance_akhir=self.balance_awal-self.jml_tab
            self.code_trans = 'TTN'








