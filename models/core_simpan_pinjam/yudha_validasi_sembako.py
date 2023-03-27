# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from  odoo.exceptions import UserError
from datetime import datetime, timedelta
import time

SESSION_STATES = [
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('valid', 'Validate')
]

class yudha_validasi_sembako(models.Model):
    _name = 'yudha.validasi.sembako'
    _order = 'no_val desc'
    _description = "yudha VALIDASI SEMBAKO"

    confirm_by = fields.Many2one('res.users',string='Confirm By',readonly='1', default=lambda self: self.env.user)
    no_val = fields.Char(string='No. Validasi',readonly=True)
    jns_dok = fields.Char(string='Jenis Dokumen', default='Validasi Sembako',index=True,copy=True,required=True, readonly=True)
    # start_date = fields.Date(string='Tanggal Awal', required=False, default=lambda self: datetime.strftime(datetime.now() - timedelta(30), '%Y-%m-%d'))
    # end_date = fields.Date(string='Tanggal Akhir', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    start_date = fields.Date(string='Tanggal Awal',required=True)
    end_date = fields.Date(string='Tanggal Akhir',required=True)
    summary_ids = fields.One2many(comodel_name='yudha.validasi.sembako.summary',inverse_name="sembako_id",string="Validasi Bulanan")
    detail_ids = fields.One2many(comodel_name='yudha.validasi.sembako.detail',inverse_name="sembako_id",string="Validasi Bulanan")
    payment_ids = fields.One2many(comodel_name='yudha.validasi.sembako.payment',inverse_name="sembako_id",string="Validasi Bulanan")
    keterangan = fields.Char(size=100, string='Keterangan')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])
    
    def name_get(self):
        result = []
        for s in self:
            name =  str(s.no_val)
            result.append((s.id, name))
        return result

    @api.onchange('start_date','end_date')
    def date_onchange(self):
        if not self.start_date:
            return
        if not self.end_date:
            return

        self.summary_ids = self._get_summary(self.start_date,self.end_date)
        self.detail_ids = self._get_detail(self.start_date,self.end_date)
        self.payment_ids = self._get_payment(self.start_date,self.end_date)

    def _get_summary(self,start_date,end_date):
        sql_query="""select a.partner_id,c.no_anggota,c.npk,c.unit_kerja,c.asal_pt,sum(a.amount) as amount
            from account_bank_statement_line a inner join account_journal b on a.journal_id=b.id 
            inner join res_partner c on a.partner_id=c.id
            where b.name='Kredit Anggota' and a.date between %s and %s
            group by a.partner_id,c.no_anggota,c.npk,c.unit_kerja,c.asal_pt order by a.partner_id;
            """
        self.env.cr.execute(sql_query, (start_date,end_date,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil=[]
            for field_rekap in result:
                rekap_lines = {
                    'partner_id': field_rekap['partner_id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': field_rekap['amount'],
                    'realisasi': field_rekap['amount'],
                    'state': 'draft',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def _get_detail(self,start_date,end_date):
        sql_query="""select a.pos_statement_id as pos_id,a.date,a.partner_id,d.product_id,d.price_unit,d.qty,d.discount,coalesce(f.amount,0) as tax,
            ((d.price_unit*d.qty)-(d.price_unit*d.qty*d.discount*0.01))*((100+coalesce(f.amount,0))*0.01)  as total_amount
            from account_bank_statement_line a inner join account_journal b on a.journal_id=b.id 
            inner join res_partner c on a.partner_id=c.id inner join pos_order_line d on a.pos_statement_id=d.order_id
            left join account_tax_pos_order_line_rel e on d.id=e.pos_order_line_id left join account_tax f on e.account_tax_id=f.id
            where b.name='Kredit Anggota' and a.date between %s and %s order by a.partner_id,a.date,a.pos_statement_id;
            """
        self.env.cr.execute(sql_query, (start_date,end_date,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil=[]
            for field_rekap in result:
                rekap_lines = {
                    'pos_id': field_rekap['pos_id'],
                    'date': field_rekap['date'],
                    'partner_id': field_rekap['partner_id'],
                    'product_id': field_rekap['product_id'],
                    'price_unit': field_rekap['price_unit'],
                    'qty': field_rekap['qty'],
                    'discount': field_rekap['discount'],
                    'tax': field_rekap['tax'],
                    'total_amount': field_rekap['total_amount'],
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def _get_payment(self,start_date,end_date):
        sql_query="""select a.pos_statement_id as pos_id,a.id as payment_id,a.partner_id,a.ref,a.date,a.amount,
            b.name as Keterangan from account_bank_statement_line a inner join account_journal b on a.journal_id=b.id 
            inner join res_partner c on a.partner_id=c.id
            where b.name='Kredit Anggota' and a.date between %s and %s order by a.partner_id,a.date,a.pos_statement_id;
            """
        self.env.cr.execute(sql_query, (start_date,end_date,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil=[]
            for field_rekap in result:
                rekap_lines = {
                    'pos_id': field_rekap['pos_id'],
                    'payment_id': field_rekap['payment_id'],
                    'partner_id': field_rekap['partner_id'],
                    'ref': field_rekap['ref'],
                    'date': field_rekap['date'],
                    'amount': field_rekap['amount'],
                    'keterangan': field_rekap['keterangan'],
                }
                semua_hasil += [rekap_lines]
            return semua_hasil


    def confirm(self):
        return

class yudha_validasi_sembako_summary(models.Model):
    _name = 'yudha.validasi.sembako.summary'

    sembako_id = fields.Many2one('yudha.validasi.sembako', string="Validasi Sembako Summary", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    amount = fields.Float('Amount', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='draft')


class yudha_validasi_sembako_detail(models.Model):
    _name = 'yudha.validasi.sembako.detail'

    sembako_id = fields.Many2one('yudha.validasi.sembako', string="Validasi Sembako ID", required=False, store=True,index=True)
    pos_id = fields.Many2one('pos.order', string='POS No', required=False)
    date = fields.Date(string='Tanggal', required=False)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    product_id = fields.Many2one('product.product', string='Nama Produk', required=False, domain="[('category_id', '=', 'Anggota')]")
    price_unit = fields.Float('Harga satuan', digits=(19, 2), default=0, required=True)
    qty = fields.Float('Quantity', digits=(19, 2), default=0, required=True)
    discount = fields.Float('Discount', digits=(19, 2), default=0, required=True)
    tax = fields.Float('PPN (%)', digits=(19, 2), default=0, required=True)
    total_amount = fields.Float('Total Harga', digits=(19, 2), default=0, required=True)

class yudha_validasi_sembako_payment(models.Model):
    _name = 'yudha.validasi.sembako.payment'

    sembako_id = fields.Many2one('yudha.validasi.sembako', string="Validasi Sembako ID", required=False, store=True,index=True)
    pos_id = fields.Many2one('pos.order', string='POS No', required=False)
    payment_id = fields.Many2one('account_bank_statement', string='Payment No', required=False)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False,domain="[('category_id', '=', 'Anggota')]")
    ref = fields.Char(size=100, string='Reference')
    date = fields.Date(string='Tanggal', required=False)
    amount = fields.Float('Jumlah', digits=(19, 2), default=0, required=True)
    keterangan = fields.Char(size=100, string='Keterangan')
