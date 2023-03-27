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

class yudha_iuran_wajib(models.Model):
    _name = 'yudha.iuran.wajib'
    _order = 'docnum desc'
    _description = "yudha IURAN WAJIB"

    docnum = fields.Char(size=100, string='No. Transaksi',readonly=True)
    nm_trans = fields.Char(size=100, string='Nama Transaksi', default='Simpanan Wajib', readonly=True)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',default='SD', help='Jenis Transaksi', required=True)
    pt_asal = fields.Many2one(comodel_name='yudha.asal.perusahaan', inverse_name='id', string="Asal Perusahaan",required=True)
    no_accmove = fields.Many2one('account.move',string='No Account Move')
    keterangan = fields.Char(size=100, string='Keterangan')
    # asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], string='Sumber Dana',
    #                              help='Sumber Dana')
    # no_rek_bank = fields.Many2one('account.journal', string='No Rekening USP', required=False, index=True,
    #                               domain="['&',('type', '=', 'bank'),('company_id','=',3)]")
    # no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    # nm_bank = fields.Char(size=100, string='Nama Bank')
    # atasnama = fields.Char(size=100, string='Atas nama')
    state = fields.Selection(string="Status", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])
    iuranwjb_ids = fields.One2many(comodel_name='yudha.iuran.wajib.details', inverse_name='iuranwjb_val',string='Iuran wajib')

    
    def name_get(self):
        result = []
        for s in self:
            name = str(s.docnum)
            result.append((s.id, name))
        return result

    
    def unlink(self):
        for line in self:
                if line.state == 'done':
                    raise ValidationError(_('Status Done tidak bisa dihapus'))
        return super(yudha_iuran_wajib, self).unlink()

    @api.onchange('pt_asal')
    def onchange_pt_asal(self):
        if not self.pt_asal:
            return
        datasimwjb = self.env['res.partner'].search([('asal_pt','=',self.pt_asal.id),('category_id','=','Anggota')])
        #datasimwjb = self.Tampil_Anggota(self.asal_pt.id)
        if not datasimwjb is None:
            self.iuranwjb_ids = []
            for alldata in datasimwjb:
                self.iuranwjb_ids = self.masuk_details(alldata.id,alldata.no_anggota,50000)


    def masuk_details(self,partid,noagt, amt):
        res = []
        res2 = []
        rekap_line = {}
        add_line = {}
        for field_rekap in self.iuranwjb_ids:
            rekap_lines = {
                'iuranwjb_val': field_rekap['iuranwjb_val'],
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'amount': field_rekap['amount'],
            }
            res2 += [rekap_lines]
        add_line = { 'iuranwjb_val': self._origin.id,
            'partner_id': partid,
            'no_agt': noagt,
            'amount': amt,
        }
        res += [add_line]
        res += res2
        return res

    # @api.onchange('asal_dana')
    # def onchange_asal_dana(self):
    #     if not self.asal_dana:
    #         return
    #     if self.asal_dana =='CS':
    #         self.no_rek_bank = []
    #         self.no_rek_agt = ''
    #         self.atasnama = ''
    #         self.nm_bank = ''


class yudha_iuran_wajib_details(models.Model):
    _name = 'yudha.iuran.wajib.details'

    iuranwjb_val = fields.Many2one(comodel_name='yudha.iuran.wajib', inverse_name='id', string="Iuran Wajib Details",required=False, store=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='No. Anggota', readonly=True)
    amount = fields.Float('Jumlah Simpanan Wajib', digits=(19, 2), default=0)


    
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
        return super(yudha_iuran_wajib_details, self).create(vals)

    
    def write(self, vals):
        if vals.get('partner_id.name', False):
            nm_agt = vals['partner_id.name']
        else:
            nm_agt = self.partner_id.name
        my_agt = self.env['res.partner'].search([('name', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
        return super(yudha_iuran_wajib_details, self).write(vals)
