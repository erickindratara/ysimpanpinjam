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
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
]

class yudha_validasi_tabungan(models.Model):
    _name = 'yudha.validasi.tabungan'

    confirm_by = fields.Many2one('res.users',string='Confirm By',readonly='1', default=lambda self: self.env.user)
    no_val = fields.Char(size=100, string='No. Validasi')
    jns_dok = fields.Char(string='Jenis Dokument', default='Validasi Tabungan',index=True,copy=True,required=True, readonly=True)
    tgl_val = fields.Date(string='Tanggal Validasi', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    tgl_periode = fields.Date(string='Tanggal Periode', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    yudhatab_ids=fields.One2many(comodel_name='yudha.validasi.tabungan.details',inverse_name="valid_id",string='yudha validasi iuran pokok')
    keterangan = fields.Char(size=100, string='Keterangan')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    def _Tampil_data(self,donum):
        if not donum:
            return
        else:
            mysql="""SELECT * FROM yudha_tabungan a WHERE a.date=%s;"""
            self.env.cr.execute(mysql, (donum,))
            result = self.env.cr.dictfetchall()
            hasil={}
            semua_hasil=[]
            if not result:
                return
            else:
                for res in result:
                    tgl = res['date']
                    teman = res['partner_id']
                    jns_trans = res['jenis_transaksi']
                    jns_tab = res['jenis_tabungan']
                    blnce_awal = res['balance_awal']
                    debt = res ['debit']
                    crdt = res['credit']
                    blnce_akhir = res['balance_akhir']
                    blnce = res['balance']
                    cd_trans = res['code_transaksi']
                    ket = res['keterangan']
                    hasil={'date': tgl,
                           'partner_id': teman,
                           'jenis_transaksi': jns_trans,
                           'jenis_tabungan': jns_tab,
                           'balance_awal': blnce_awal,
                           'debit': debt,
                           'credit': crdt,
                           'balance_akhir': blnce_akhir,
                           'balance': blnce,
                           'code_transaksi': cd_trans,
                           'keterangan': ket}
                    semua_hasil +=[hasil]
                return semua_hasil

    @api.onchange('tgl_periode')
    def onchange_tgl_periode(self):
        if not self.tgl_periode:
            return
        self.yudhatab_ids = self._Tampil_data(self.tgl_periode)

    
    def validate(self):
        if self.state == 'draft':
            # for alldata in self.yudhatab_ids:
            #     if alldata.balance_awal==alldata.balance_akhir:
            #         raise ValidationError(_('Balance Awal sama dengan Balance Akhir, tidak bisa di validasi'))
            #update saldo tabungan di res_partner
            #totsaldo=0
            for allline in self.yudhatab_ids:
                res_partner_obj = self.env['res.partner'].search([('id', '=', allline.partner_id.id)])
                res_partner_obj.write({'saldo_tabungan': allline.balance_akhir})
                if allline.jenis_transaksi == 'setoran':
                    #totsaldo = totsaldo + allline.credit
                    self.buat_jurnal_masuk(allline.jenis_tabungan,allline.credit)
                else:
                    self.buat_jurnal_keluar(allline.jenis_tabungan, allline.debit)
            self.write({'state': 'confirm'})
            self.state = SESSION_STATES[1][0]

    def get_last_journal(self):
        #mmsql = """SELECT count(name) FROM account_move;"""
        mmsql="""SELECT max(id) FROM account_move;"""
        self.env.cr.execute(mmsql,)
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return 0

    def buat_jurnal_masuk(self,jenistab,jumlah):
        if not jenistab:
            return
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []
        acc_line = {}
        jid= self.env['account.journal'].search([('name','=','Unit Simpan Pinjam')],limit=1)
        tahun = datetime.now().year
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARTAB',tahun,  counter)
        acc_header={'date':fields.datetime.now(),
                    'journal_id': jid.id,
                    'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                    'name': namaaccount }
        myanal = self.env['account.analytic.account'].search([('name', '=', '300 - Unit Simpan Pinjam')], limit=1)
        for x in range(0, 2):
            if x == 0:
                if jenistab == 'Tabungan Masyarakat':
                    myacc = self.env['account.account'].search([('name','=','TABUNGAN MASYARAKAT')])
                elif jenistab == 'Tabungan Anggota':
                    myacc = self.env['account.account'].search([('name', '=', 'TABUNGAN ANGGOTA')])
                else:
                    myacc = self.env['account.account'].search([('name', '=', 'TABUNGAN KHUSUS')])

                acc_line={'account_id': myacc.id,
                           'name': '',
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'debit': 0,
                           'credit': jumlah}
            else:
                accid = self.env['account.account'].search([('name', '=', 'KAS UNIT SIMPAN PINJAM')])
                #agus
                acc_line={'account_id': int(accid),
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'name': '',
                           'debit': jumlah,
                           'credit': 0}
            acc_item2.append((0, 0, acc_line))
            acc_header['line_ids'] = acc_item2
        # print('buat jurnal kelar', acc_header)
        buat_jurnal=self.env['account.move'].create(acc_header)
        buat_jurnal.post()

    def buat_jurnal_keluar(self,jenistab,jumlah):
        if not jenistab:
            return
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []
        acc_line = {}
        jid= self.env['account.journal'].search([('name','=','Unit Simpan Pinjam')],limit=1)
        tahun = datetime.now().year
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARTAB',tahun,  counter)
        acc_header={'date':fields.datetime.now(),
                    'journal_id': jid.id,
                    'ref': 'Akumulasi penarikan tabungan dan simpanan',
                    'name': namaaccount }
        myanal = self.env['account.analytic.account'].search([('name','=','300 - Unit Simpan Pinjam')],limit=1)
        for x in range(0, 2):
            if x == 0:
                if jenistab == 'Tabungan Masyarakat':
                    myacc = self.env['account.account'].search([('name','=','TABUNGAN MASYARAKAT')])
                elif jenistab == 'Tabungan Anggota':
                    myacc = self.env['account.account'].search([('name', '=', 'TABUNGAN ANGGOTA')])
                else:
                    myacc = self.env['account.account'].search([('name', '=', 'TABUNGAN KHUSUS')])

                acc_line={'account_id': myacc.id,
                           'name': '',
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'debit': jumlah,
                           'credit': 0}
            else:
                accid = self.env['account.account'].search([('name', '=', 'KAS UNIT SIMPAN PINJAM')])
                acc_line={'account_id': int(accid),
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'name': '',
                           'debit': 0,
                           'credit': jumlah}
            acc_item2.append((0, 0, acc_line))
            acc_header['line_ids'] = acc_item2
        # print('buat jurnal kelar', acc_header)
        buat_jurnal=self.env['account.move'].create(acc_header)
        buat_jurnal.post()


class yudha_validasi_tabungan_details(models.Model):
    _name = 'yudha.validasi.tabungan.details'

    valid_id= fields.Many2one(comodel_name='yudha.validasi.tabungan',inverse_name='id', string="Validasi Timbang I Details", required=False,store=True,index=True )
    date = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True,index=True,domain="[('category_id.name', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    amount = fields.Float('Jumlah Iuran Pokok', digits=(19, 2), default=0)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    dok_pen  = fields.Char(size=100, string='Dokument Pendukung')