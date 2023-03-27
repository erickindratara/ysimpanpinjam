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

class yudha_register_tabungan(models.Model):
    _name = 'yudha.register.tabungan'
    _order = 'no_rekening desc'
    _description = "REGISTER TABUNGAN"

    tanggal = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jenis_tabungan = fields.Many2one(comodel_name="yudha.master.jenis.tabungan",inverse_name='id', string="Jenis Tabungan", required=True, index=True)
    no_agt = fields.Char(size=100, string='No. Anggota')
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]")
    no_rekening = fields.Char(size=100, readonly=True, string='No. Rekening')
    atasnama = fields.Char(size=100, string='Atas nama')
    keterangan = fields.Char(size=100, string='Keterangan')
    state = fields.Boolean(string='Active')

    def toggle_active(self):
        if self.state==False:
            self.state = True
        else:
            self.state = False

    def unlink(self):
        for line in self:
            raise ValidationError(_('No Rekening tidak bisa dihapus'))

    def name_get(self):
        result = []
        for s in self:
            name =  str(s.no_rekening)
            result.append((s.id, name))
        return result

    @api.model
    def create(self, vals):

        # myquery = """SELECT count(1)+1 FROM yudha_register_tabungan where partner_id=%s;"""
        # self.env.cr.execute(myquery,)
        # tot_rek = self.env.cr.fetchone()[0]
        # if tot_rek<10:
        #     tot_rek='0'+tot_rek
        jenis_tabungan=vals['jenis_tabungan']
        myquery = """SELECT count(1)+1 FROM yudha_register_tabungan where jenis_tabungan=%s;"""
        self.env.cr.execute(myquery,(jenis_tabungan,))
        no_urut = self.env.cr.fetchone()[0]
        no_agt=vals['no_agt']
        asal_pt=self.env['res.partner'].search([('id','=',vals['partner_id'])]).asal_pt
        if asal_pt.id==False:
            raise ValidationError(_('Asal Perusahaan belum di setting di master anggota'))

        kode_tabungan = self.env['yudha.master.jenis.tabungan'].search([('id','=',jenis_tabungan)]).kode_tabungan
        kode_nasabah = self.env['yudha.asal.perusahaan'].search([('id','=',asal_pt.id)]).kode_nasabah
        # 0724-00-12345-01
        no_akhir=''
        if no_urut < 10:
            no_akhir = no_agt +'-'+kode_tabungan+'-'+ '0000' + str(no_urut) +'-'+ kode_nasabah
        elif no_urut < 100:
            no_akhir = no_agt +'-'+kode_tabungan+ '-'+'000' + str(no_urut) + '-'+kode_nasabah
        elif no_urut < 1000:
            no_akhir = no_agt +'-'+kode_tabungan+ '-'+'00' + str(no_urut) + '-'+kode_nasabah
        elif no_urut < 10000:
            no_akhir = no_agt +'-'+kode_tabungan+ '-'+'0' + str(no_urut) +'-'+ kode_nasabah
        elif no_urut >= 10000:
            no_akhir = no_agt +'-'+kode_tabungan+ '-'+str(no_urut) + '-'+kode_nasabah

        vals['no_rekening'] = no_akhir
        vals['state'] = True
        return super(yudha_register_tabungan, self).create(vals)

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
        my_agt = self.env['res.partner'].search([('id','=', self.partner_id.id)])
        if my_agt.id != False:
            self.no_agt = my_agt.no_anggota
            self.no_rek_agt = my_agt.no_rek_agt
            self.nm_bank = my_agt.nm_bank
            self.atasnama = my_agt.atas_nama

