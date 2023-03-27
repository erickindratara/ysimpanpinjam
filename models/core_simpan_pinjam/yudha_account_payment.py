# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    loan_type = fields.Selection([('dana','Pinjaman Dana'),('barang','Pinjaman Barang'),('konsumtif','Pinjaman Konsumtif'),('syariah','Pinjaman Syariah'),('tarikan_deposito','Tarikan Deposito'),('tarikan_tabungan','Tarikan Tabungan')], string='Type Tarikan')
    dana_id = fields.Many2one('yudha.peminjaman.dana', 'No Pinjaman Dana')
    barang_id = fields.Many2one('yudha.peminjaman.barang', 'No Pinjaman Barang')
    konsumtif_id = fields.Many2one('yudha.peminjaman.konsumtif', 'No Pinjaman Konsumtif')
    syariah_id = fields.Many2one('yudha.peminjaman.syariah', 'No Pinjaman Syariah')
    deposito_id = fields.Many2one('yudha.deposito', 'No Transaksi')
    tabungan_id = fields.Many2one('yudha.tabungan', 'No Transaksi')

    @api.onchange('partner_id')
    def onchange_partner_id_dana(self):
        if not self.partner_id:
            return
        self.loan_type=[]
        self.dana_id = []
        self.barang_id = []
        self.konsumtif_id = []
        self.syariah_id = []
        self.deposito_id = []
        self.tabungan_id = []

    @api.onchange('dana_id','barang_id','konsumtif_id','sembako_id','syariah_id','deposito_id','tabungan_id')
    def onchange_pinjaman_id(self):
        if self.loan_type == 'dana':
            self.amount = self.dana_id.jml_pinjam
        elif self.loan_type == 'barang':
            self.amount = self.barang_id.jml_pinjam
        elif self.loan_type == 'konsumtif':
            self.amount = self.konsumtif_id.jml_pinjam
        elif self.loan_type == 'syariah':
            self.amount = self.syariah_id.jml_pinjam
        elif self.loan_type == 'tarikan_deposito':
            self.amount = self.deposito_id.jml_depo
        elif self.loan_type == 'tarikan_tabungan':
            self.amount = self.tabungan_id.jml_tab

    @api.onchange('loan_type')
    def onchange_loan_type(self):
        if not self.partner_id:
            return
        if not self.loan_type:
            return
        if self.loan_type=='dana':
            sql_query = """select id from yudha_peminjaman_dana where state='valid' and partner_id=%s
                        """
        elif self.loan_type=='barang':
            sql_query = """select id from yudha_peminjaman_barang where state='valid' and partner_id=%s
                        """
        elif self.loan_type=='konsumtif':
            sql_query = """select id from yudha_peminjaman_konsumtif where state='valid' and partner_id=%s
                        """
        elif self.loan_type=='syariah':
            sql_query = """select id from yudha_peminjaman_syariah where state='valid' and partner_id=%s
                        """
        elif self.loan_type == 'tarikan_deposito':
            sql_query = """select distinct a.id from yudha_deposito a inner join yudha_pencairan_deposito b on a.id=b.depo_id where b.type_bayar='transfer' and a.state='payment' and a.partner_id=%s
                        """
        elif self.loan_type == 'tarikan_tabungan':
            sql_query = """select id from yudha_tabungan where jns_trans='TD' and asal_dana='TF' and state='valid' and partner_id=%s
                        """

        self.env.cr.execute(sql_query, (self.partner_id.id,))
        res_id = self.env.cr.dictfetchall()
        data_list = []
        coa_kliring_pinjaman=self.env['yudha.settings'].search([('code','=','settings')], limit=1).coa_kliring_pinjaman
        coa_kliring_tarikan=self.env['yudha.settings'].search([('code','=','settings')], limit=1).coa_kliring_tarikan
        if res_id != False:
            for field in res_id:
                data_list.append(field['id'])
        if self.loan_type=='dana':
            self.barang_id=[]
            self.konsumtif_id=[]
            self.sembako_id=[]
            self.syariah_id=[]
            self.deposito_id=[]
            self.tabungan_id=[]
            self.control_account=coa_kliring_pinjaman
            return {'domain': {'dana_id': [('id', '=', data_list)]}}
        elif self.loan_type=='barang':
            self.dana_id=[]
            self.konsumtif_id=[]
            self.sembako_id=[]
            self.syariah_id=[]
            self.deposito_id = []
            self.tabungan_id = []
            self.control_account=coa_kliring_pinjaman
            return {'domain': {'barang_id': [('id', '=', data_list)]}}
        elif self.loan_type=='konsumtif':
            self.barang_id=[]
            self.dana_id=[]
            self.sembako_id=[]
            self.syariah_id=[]
            self.deposito_id = []
            self.tabungan_id = []
            self.control_account=coa_kliring_pinjaman
            return {'domain': {'konsumtif_id': [('id', '=', data_list)]}}
        elif self.loan_type=='syariah':
            self.barang_id=[]
            self.konsumtif_id=[]
            self.sembako_id=[]
            self.dana_id=[]
            self.deposito_id = []
            self.tabungan_id = []
            self.control_account=coa_kliring_pinjaman
            return {'domain': {'syariah_id': [('id', '=', data_list)]}}
        elif self.loan_type=='tarikan_deposito':
            self.barang_id=[]
            self.konsumtif_id=[]
            self.sembako_id=[]
            self.dana_id=[]
            self.syariah_id = []
            self.tabungan_id = []
            self.control_account=coa_kliring_tarikan
            return {'domain': {'deposito_id': [('id', '=', data_list)]}}
        elif self.loan_type=='tarikan_tabungan':
            self.barang_id=[]
            self.konsumtif_id=[]
            self.sembako_id=[]
            self.dana_id=[]
            self.syariah_id = []
            self.deposito_id = []
            self.control_account=coa_kliring_tarikan
            return {'domain': {'tabungan_id': [('id', '=', data_list)]}}


    def post(self):
        if self.control_account.name=='KLIRING PINJAMAN ANGGOTA':
            if not self.loan_type:
                raise UserError('Type Tarikan harus diisi')

        if self.loan_type=='dana':
            if not self.dana_id:
                raise UserError('No Pinjaman harus diisi')

        yudha_obj=self.env['yudha.peminjaman.dana'].search([('id','=',self.dana_id.id)])
        if yudha_obj:
            yudha_obj.write({'state': 'paid'})
            yudha_obj_detail = self.env['yudha.peminjaman.dana.details'].search([('loan_id','=',yudha_obj.id),('doc_type','=','outbound'), ('cicilan_ke', '=', 0)])
            yudha_obj_detail.write({'payment_id':self.id,'state':'paid','jml_cicilan' : -self.amount})
        elif self.loan_type=='barang':
            if not self.barang_id:
                raise UserError('No Pinjaman harus diisi')
            yudha_obj = self.env['yudha.peminjaman.barang'].search([('id', '=', self.barang_id.id)])
            if yudha_obj:
                yudha_obj.write({'state': 'paid'})
                yudha_obj_detail = self.env['yudha.peminjaman.barang.details'].search(
                    [('loan_id', '=', yudha_obj.id), ('doc_type', '=', 'outbound'), ('cicilan_ke', '=', 0)])
                yudha_obj_detail.write({'payment_id': self.id,'state':'paid','jml_cicilan' : -self.amount})
        elif self.loan_type=='konsumtif':
            if not self.konsumtif_id:
                raise UserError('No Pinjaman harus diisi')
            yudha_obj = self.env['yudha.peminjaman.konsumtif'].search([('id', '=', self.konsumtif_id.id)])
            if yudha_obj:
                yudha_obj.write({'state': 'paid'})
                yudha_obj_detail = self.env['yudha.peminjaman.konsumtif.details'].search(
                    [('loan_id', '=', yudha_obj.id), ('doc_type', '=', 'outbound'), ('cicilan_ke', '=', 0)])
                yudha_obj_detail.write({'payment_id': self.id,'state':'paid','jml_cicilan' : -self.amount})
        elif self.loan_type=='syariah':
            if not self.syariah_id:
                raise UserError('No Pinjaman harus diisi')
            yudha_obj = self.env['yudha.peminjaman.syariah'].search([('id', '=', self.syariah_id.id)])
            if yudha_obj:
                yudha_obj.write({'state': 'paid'})
                yudha_obj_detail = self.env['yudha.peminjaman.syariah.details'].search(
                    [('loan_id', '=', yudha_obj.id), ('doc_type', '=', 'outbound'), ('cicilan_ke', '=', 0)])
                yudha_obj_detail.write({'payment_id': self.id,'state':'paid','jml_cicilan' : -self.amount})
        elif self.loan_type=='tarikan_deposito':
            if not self.syariah_id:
                raise UserError('No Transaksi harus diisi')
            yudha_obj = self.env['yudha.deposito'].search([('id', '=', self.deposito_id.id)])
            if yudha_obj:
                yudha_obj.write({'state': 'paid'})
                yudha_obj_detail = self.env['yudha.pencairan.deposito'].search([('depo_id', '=', self.deposito_id.id)])
                yudha_obj_detail.write({'state':'paid'})

        return super(AccountPayment, self).post()
