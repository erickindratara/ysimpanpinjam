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

SESSION_STATES = [
        ('ready', 'Ready'),
        ('done', 'Done')
]

class yudha_iuran_wajib_setor(models.Model):
    _name = 'yudha.iuran.wajib.setor'
    _order = 'docnum desc'
    _description = "yudha IURAN WAJIB SETOR"

    docnum = fields.Char(size=100, string='No. Transaksi',readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Simpanan Wajib', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    keterangan = fields.Char(size=100, string='Keterangan')
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',default='SD', help='Jenis Transaksi')
    no_accmove = fields.Many2one('account.move',string='No Account Move')
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='No. Anggota')
    amount = fields.Float('Jumlah Simpanan Wajib', digits=(19, 2), default='0', readonly=True)
    asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer'), ('PG', 'Potong Gaji')], string='Sumber Dana',
                                 help='Sumber Dana')
    no_rek_bank = fields.Many2one('account.journal', string='No Rekening USP', required=False, index=True,
                                  domain="['&',('type', '=', 'bank'),('company_id','=',3)]")
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    atasnama = fields.Char(size=100, string='Atas nama')

    state = fields.Selection(string="Status", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    
    def name_get(self):
        result = []
        for s in self:
            name =  str(s.docnum)
            result.append((s.id, name))
        return result

    
    def unlink(self):
        for line in self:
                if line.state == 'done':
                    raise ValidationError(_('Status Done tidak bisa dihapus'))
        return super(yudha_iuran_wajib_setor, self).unlink()

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

        myquery = """SELECT max(docnum) FROM yudha_iuran_wajib_setor;"""
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
            vals['docnum'] = 'SIMPOK/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] ='SIMPOK/'+ str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
        simp_wajib = settings_obj.simp_wajib
        vals['amount'] = simp_wajib
        return super(yudha_iuran_wajib_setor, self).create(vals)

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

        settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
        simp_wajib = settings_obj.simp_wajib
        self.amount = simp_wajib

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('id','=', self.partner_id.id)])
        if my_agt.id != False:
            self.no_agt = my_agt.no_anggota
            self.no_rek_agt = my_agt.no_rek_agt
            self.nm_bank = my_agt.nm_bank
            self.atasnama = my_agt.atas_nama

        settings_obj=self.env['yudha.settings'].search([('code','=','settings')], limit=1)
        simp_wajib = settings_obj.simp_wajib
        self.amount=simp_wajib

    @api.onchange('asal_dana')
    def onchange_asal_dana(self):
        if not self.asal_dana:
            return
        if self.asal_dana =='CS':
            self.no_rek_bank = []
            self.no_rek_agt = ''
            self.atasnama = ''
            self.nm_bank = ''