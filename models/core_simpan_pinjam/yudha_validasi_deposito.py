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

class yudha_validasi_deposito(models.Model):
    _name = 'yudha.validasi.deposito'

    confirm_by = fields.Many2one('res.users', string='Confirm By', readonly='1', default=lambda self: self.env.user)
    interdoc=fields.Char(string='No Validasi', default=lambda self: self.env['ir.sequence'].next_by_code('yudha.validasi.tabungan.1'),index=True,copy=True,required=True)
    tgl_val = fields.Date(string='Tanggal Validasi', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    yudhadepo_ids=fields.One2many(comodel_name='yudha.validasi.deposito.details',inverse_name="valid_id",string='yudha validasi iuran pokok')
    tgl_periode = fields.Date(string='Tanggal Periode', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    state = fields.Selection(string="State", selection=SESSION_STATES, required=True, readonly=True, store=True, default=SESSION_STATES[0][0])


    def _Tampil_data(self,donum):
        if not donum:
            return
        else:
            mysql="""SELECT * FROM yudha_deposito a WHERE a.date=%s;"""
            self.env.cr.execute(mysql, (donum,))
            result = self.env.cr.dictfetchall()
            hasil={}
            semua_hasil=[]
            if not result:
                return
            else:
                for res in result:
                    tgl = res['date']
                    dep_no = res['deposito_no']
                    part_id = res['partner_id']
                    lm_depo = res['lama_deposito']
                    byr_bung = res['bunga_dibayarkan']
                    bunga = res['bunga']
                    base = res['base_bunga']
                    recur = res['recurring']
                    dbt = res['debit']
                    crdt = res['credit']
                    ket = res['keterangan']
                    stat = res['status_deposito']
                    hasil={'date': tgl,
                           'deposito_no': dep_no,
                           'partner_id': part_id,
                           'lama_deposito': lm_depo,
                           'bunga _dibayarkan': byr_bung,
                           'bunga': bunga,
                           'base_bunga': base,
                           'recurring': recur,
                           'credit': crdt,
                           'keterangan': ket,
                           'status_deposito': stat}
                    semua_hasil +=[hasil]
                return semua_hasil

    @api.onchange('tgl_periode')
    def onchange_tgl_periode(self):
        if not self.tgl_periode:
            return
        self.yudhadepo_ids = self._Tampil_data(self.tgl_periode)


    
    def validate(self):

        if self.state == 'draft':
            for allline in self.yudhadepo_ids:
                if allline.credit == 0:
                    raise ValidationError(_('Jumlah Deposito 0, tidak bisa di validasi'))

                #update saldo deposito di res_partner
                res_partner_obj = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
                saldo_deposito = res_partner_obj.saldo_deposito
                saldo_deposito = saldo_deposito + self.credit
                res_partner_obj.write({'saldo_deposito': saldo_deposito})
                self.status_deposito = 'Active'
                if self.debit > 0:
                    self.buat_jurnal_keluar(self.lama_deposito, self.debit)
                else:
                    self.buat_jurnal_masuk(self.lama_deposito,self.credit)

            self.write({'state': 'confirm'})
            self.state = SESSION_STATES[1][0]
    def _update_status(self,nodepo,stat):
        if not nodepo:
            return

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
        print('line122', jenistab)
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []
        acc_line = {}
        jid= self.env['account.journal'].search([('name','=','Unit Simpan Pinjam')],limit=1)
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date = datetime.strptime(self.date, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARDPST',tahun,  counter)
        acc_header={'date':fields.datetime.now(),
                    'journal_id': jid.id,
                    'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                    'name': namaaccount }
        myanal = self.env['account.analytic.account'].search([('name', '=', '300 - Unit Simpan Pinjam')], limit=1)
        for x in range(0, 2):
            if x == 0:
                if jenistab == 1:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 1 BULAN')])
                elif jenistab == 3:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 3 BULAN')])
                elif jenistab == 6:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 6 BULAN')])
                else:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 12 BULAN')])

                acc_line={'account_id': myacc.id,
                           'name': '',
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'debit': 0,
                           'credit': jumlah}
            else:
                accid = self.env['account.account'].search([('name', '=', 'KAS UNIT SIMPAN PINJAM')])
                acc_line={'account_id': accid.id,
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
        print('line175', jenistab)
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []
        acc_line = {}
        jid= self.env['account.journal'].search([('name','=','Unit Simpan Pinjam')],limit=1)
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date = datetime.strptime(self.date, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARDPST',tahun,  counter)
        acc_header={'date':fields.datetime.now(),
                    'journal_id': jid.id,
                    'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                    'name': namaaccount }
        myanal = self.env['account.analytic.account'].search([('name', '=', '300 - Unit Simpan Pinjam')], limit=1)
        for x in range(0, 2):
            if x == 0:
                if jenistab == 1:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 1 BULAN')])
                elif jenistab == 3:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 3 BULAN')])
                elif jenistab == 6:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 6 BULAN')])
                else:
                    myacc = self.env['account.account'].search([('name', '=', 'SIMPANAN BERJANGKA 12 BULAN')])
                acc_line={'account_id': myacc.id,
                           'name': '',
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'debit': 0,
                           'credit': jumlah}
            else:
                accid = self.env['account.account'].search([('name', '=', 'KAS UNIT SIMPAN PINJAM')])
                #agus
                acc_line={'account_id': accid.id,
                           'partner_id': self._get_partner_id_by_docname(self.docnum.name),
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


class yudha_validasi_deposito_details(models.Model):
    _name = 'yudha.validasi.deposito.details'

    valid_id= fields.Many2one(comodel_name='yudha.validasi.deposito',inverse_name='id', string="Validasi Deposito Details", required=False,store=True,index=True )
    date = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    deposito_no = fields.Char(string="Nomor Deposito", length=30)
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True,index=True,domain="[('category_id.name', '=', 'Anggota')]")
    lama_deposito = fields.Integer('Lama Deposito (Bulan)', default=0, required=True)
    bunga_dibayarkan = fields.Integer('Bunga dibayarkan (Bulan)', default=0, required=True)
    bunga = fields.Float('Bunga/th (%)', digits=(19, 2), default=0, required=True)
    base_bunga = fields.Selection([('global', 'Global'), ('document', 'Dokumen')], default='global',string='Base Bunga', required=True)
    recurring = fields.Boolean(required=False, default=False, string='Perpanjang Otomatis')
    debit = fields.Float('Jumlah Pencairan', digits=(19, 2), default=0)
    credit = fields.Float('Jumlah Deposito', digits=(19, 2), default=0)
    keterangan = fields.Char(size=100, string='Keterangan')
    status_deposito = fields.Char(size=100, string='Status Deposito')
