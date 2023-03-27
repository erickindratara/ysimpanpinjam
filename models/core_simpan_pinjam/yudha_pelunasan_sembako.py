# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, ValidationError

SESSION_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirm'),
    ('valid', 'Validate')
]


class yudha_PelunasanSembako(models.Model):
    _name = 'yudha.pelunasan.sembako'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.sembako", inverse_name='id', string="Loan Id", required=False, default=False)
    date_pay = fields.Date(string='Tanggal Payment', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], string='Type',default='outbound')
    asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], string='Sumber Dana',help='Sumber Dana',required=True)
    amount = fields.Float('Jumlah', digits=(16, 2), default=0)
    description = fields.Char(size=200,default='')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    @api.model
    def default_get(self, fields):
        loan_id = self._context.get('loan_ids')
        rec = super(yudha_PelunasanSembako, self).default_get(fields)
        if loan_id:
            rec.update({'loan_id': loan_id[0]})

        return rec

    
    def post_pelunasan(self):
        if self.date_pay == False:
            raise ValidationError(_('Tanggal harus diisi'))
        if self.asal_dana == []:
            raise ValidationError(_('Asal Dana harus dipilih'))
        if self.amount <= 0:
            raise ValidationError(_('Jumlah Pelunasan harus lebih besar dari 0'))

        loan_id = self.loan_id.id
        date_pay = self.date_pay
        doc_type = 'inbound'
        asal_dana = self.asal_dana
        amount = self.amount
        description = self.description
        state = 'confirm'

        lunas_obj = self.env['yudha.pelunasan.sembako']
        lunas_obj.create({
            'loan_id': loan_id,
            'date_pay': date_pay,
            'doc_type': doc_type,
            'asal_dana': asal_dana,
            'amount': amount,
            'description': description,
            'state': state,
        })
        yudha_obj = self.env['yudha.peminjaman.sembako'].search([('id', '=', loan_id)])
        cicilan_ke = yudha_obj.lama_cicilan - yudha_obj.sisa_cicilan + 1
        pinjam_obj = self.env['yudha.peminjaman.sembako.details']
        pinjam_obj.create({
            'loan_id': loan_id,
            'date_pay': date_pay,
            'doc_type': doc_type,
            'type_pelunasan': 'cash',
            'jml_cicilan': amount,
            'cicilan_ke': cicilan_ke,
            'description': description,
        })
        jml_bayar = yudha_obj.jml_bayar + amount
        sisa_loan = yudha_obj.sisa_loan - amount
        jml_cicilan = yudha_obj.jml_cicilan
        sisa_cicilan = sisa_loan / jml_cicilan
        yudha_obj.write({
            'jml_bayar': jml_bayar,
            'sisa_pinjaman': sisa_loan,
            'sisa_cicilan': sisa_cicilan,
        })
        if sisa_loan == 0:
            yudha_obj.write({'state': 'done'})

        self.write({'state': 'paid'})

