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

class yudha_validasi_iuran_wajib(models.Model):
    _name = 'yudha.validasi.iuran.wajib'

    confirm_by = fields.Many2one('res.users',string='Confirm By',readonly='1', default=lambda self: self.env.user)
    no_val = fields.Char(size=100, string='No. Validasi')
    jns_dok = fields.Char(string='Jenis Dokument', default='Validasi Simpanan Wajib',index=True,copy=True,required=True, readonly=True)
    tgl_val = fields.Date(string='Tanggal Validasi', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    tgl_periode = fields.Date(string='Tanggal Periode', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    keterangan = fields.Char(size=100, string='Keterangan')
    iuranw_ids=fields.One2many(comodel_name='yudha.validasi.iuran.wajib.details',inverse_name="valid_id",string='yudha validasi iuran pokok')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])



    def _Tampil_data(self,donum):
        if not donum:
            return
        else:
            mysql="""SELECT * FROM yudha_iuran_wajib a WHERE a.date=%s;"""
            self.env.cr.execute(mysql, (donum,))
            result = self.env.cr.dictfetchall()
            hasil={}
            semua_hasil=[]
            if not result:
                return
            else:
                for res in result:
                    idnya = res['id']
                    tgl=res['date']
                    partid=res['partner_id']
                    jml=res['amount']
                    ket=res['keterangan']
                    hasil={'valid_id': idnya,
                           'date': tgl,
                           'partner_id': partid,
                           'amount': jml,
                           'keterangan': ket}
                    semua_hasil +=[hasil]
                return semua_hasil

    @api.onchange('tgl_periode')
    def onchange_tgl_periode(self):
        if not self.tgl_periode:
            return
        self.iuranw_ids = self._Tampil_data(self.tgl_periode)

    
    def unlink(self):
        for line in self.iuranw_ids:
            if line.amount != 0:
                if line.state != 'draft':
                    raise ValidationError(_('Status Confirm tidak bisa dihapus'))
        return super(yudha_validasi_iuran_wajib, self).unlink()

    
    def validate(self):
        if self.state == 'draft':
            for alldata in self.iuranw_ids:
                if alldata.amount == 0:
                    raise ValidationError(_('Jumlah Iuran 0, tidak bisa di validasi'))
            totsaldo = 0
            for alline in self.iuranw_ids:
                # update saldo iuran wajib di res_partner
                res_partner_obj = self.env['res.partner'].search([('id', '=', alline.partner_id.id)])
                iuran_wajib = res_partner_obj.iuran_wajib
                iuran_wajib = iuran_wajib + alline.amount
                res_partner_obj.write({'iuran_wajib': iuran_wajib})
                totsaldo = totsaldo + alline.amount
            self.buat_jurnal(totsaldo,self.tgl_periode)
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

    def buat_jurnal(self,jumlah,tglbuat):
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date = datetime.strptime(tglbuat, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []
        acc_line = {}
        #mycompid = self.env['res.users'].search([('id','=',self.env.uid)],limit=1)
        mycompid = self.env['res.company'].search([('name', 'ilike', 'unit simpan pinjam')], limit=1)
        compid = self.env['res.users'].search([('id','=',self.env.uid)],limit=1)
        #namalengkap='[%s] %s' %(self.env['product.product'].search([('product_tmpl_id','=',prodid)],limit=1).default_code,self.env['product.template'].search([('id','=',prodid)],limit=1).name)
        jid= self.env['account.journal'].search([('name','=','Unit Simpan Pinjam'),('company_id','=',mycompid.id)],limit=1)
        # print('line 70',mycompid.id)
        # print('line 71',jid.id)
        #tahun = datetime.now().year
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('SIMPOK',tahun,  counter)
        acc_header={'date':fields.datetime.now(),
                    'journal_id': jid.id,
                    'company_id': mycompid.id,
                    'ref': 'test',
                    'name': namaaccount }
        myanal = self.env['account.analytic.account'].search(['&',('name','ilike','unit simpan pinjam'),('company_id','=',mycompid.id)],limit=1)
        for x in range(0, 2):
            if x == 0:
                myacc = self.env['account.account'].search(['&',('name', '=', 'SIMPANAN WAJIB ANGGOTA'),('company_id','=',mycompid.id)])
                #print('line 89', myacc.id)
                acc_line={'account_id': myacc.id,
                           'name': '',
                          'company_id': mycompid.id,
                           'analytic_account_id': myanal.id,
                           'analytic_tag_ids': '',
                           'debit': 0,
                           'credit': jumlah}
            else:
                #accid = self.env['account.account'].search(['&',('name', '=', 'KAS UNIT SIMPAN PINJAM'),('company_id','=',compid.company_id.id)])
                accid = self.env['account.account'].search(['&',('name', '=', 'KAS UNIT SIMPAN PINJAM'),('company_id','=',mycompid.id)])
                #print('line 99', accid.id)
                acc_line={'account_id': accid.id,
                           'company_id': mycompid.id,
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



class yudha_validasi_iuran_wajib_details(models.Model):
    _name = 'yudha.validasi.iuran.wajib.details'

    valid_id= fields.Many2one(comodel_name='yudha.validasi.iuran.wajib',inverse_name='id', string="Validasi Iuran Wajib Details", required=False,store=True,index=True )
    date = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True,index=True,domain="[('category_id.name', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    amount = fields.Float('Jumlah Iuran Pokok', digits=(19, 2), default=0)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    dok_pen  = fields.Char(size=100, string='Dokument Pendukung')