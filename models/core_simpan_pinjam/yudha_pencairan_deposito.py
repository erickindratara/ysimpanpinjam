# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
import time
import calendar
from datetime import datetime

SESSION_STATES = [
    ('ready', 'Ready'),
    ('valid', 'Validate'),
    ('done', 'Done')
]


class yudha_PencairanDeposito(models.Model):
    _name = 'yudha.pencairan.deposito'

    depo_id = fields.Many2one(comodel_name="yudha.deposito", inverse_name='id', string="Depo Id", required=False, default=False)
    tgl_depo = fields.Date(string='Tanggal Deposito', readonly=True,default=lambda self: time.strftime("%Y-%m-%d"))
    jatuh_tempo = fields.Date(string='Jatuh Tempo', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    jml_depo = fields.Float('Jumlah Deposito', digits=(16, 2), readonly=True, store=True, default=0)
    date_trans = fields.Date(string='Tanggal Pencairan', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    type_bayar = fields.Selection([('tabungan', 'Tabungan'), ('transfer', 'Transfer')], string='Type Pembayaran',default='tabungan')
    amount = fields.Float('Jumlah Pecairan', digits=(16, 2), default=0)
    description = fields.Char(size=200,default='')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    @api.model
    def default_get(self, fields):
        depo_id = self._context.get('depo_ids')
        depo_obj = self.env['yudha.deposito'].search([('id','=',depo_id[0])])
        rec = super(yudha_PencairanDeposito, self).default_get(fields)
        if depo_id:
            rec.update({'depo_id': depo_id[0]})
            rec.update({'tgl_depo': depo_obj.tgl_trans})
            rec.update({'jml_depo': depo_obj.jml_depo})
            rec.update({'jatuh_tempo': depo_obj.jatuh_tempo})
            rec.update({'amount': depo_obj.jml_depo})
        return rec

    @api.onchange('amount')
    def amount_onchange(self):
        if self.amount!=self.jml_depo:
            self.amount=self.jml_depo

    
    def post_pencairan_deposito(self):
        if self.date_trans == False:
            raise UserError(_('Tanggal harus diisi'))
        if self.type_bayar == []:
            raise UserError(_('Type Pembayaran harus dipilih'))
        if self.amount != self.jml_depo:
            raise UserError(_('Jumlah Pecairan harus sama dengan Jumlah Deposito'))

        depo_id = self.depo_id.id
        tgl_depo = self.tgl_depo
        jatuh_tempo = self.jatuh_tempo
        jml_depo = self.jml_depo
        date_trans = self.date_trans
        type_bayar = self.type_bayar
        amount = self.amount
        description = self.description

        delta = date_trans - tgl_depo
        bulan_ke = delta.months

        cair_obj = self.env['yudha.pencairan.deposito']
        cair_obj.create({
            'depo_id': depo_id,
            'tgl_depo': tgl_depo,
            'jatuh_tempo': jatuh_tempo,
            'jml_depo': jml_depo,
            'date_trans': date_trans,
            'type_bayar': type_bayar,
            'amount': amount,
            'description': description,
            'state': 'ready',
        })
        yudha_obj = self.env['yudha.deposito'].search([('id', '=', depo_id)])
        yudha_obj.write({'state':'done'})
        DATETIME_FORMAT = "%Y-%m-%d"
        date_trans = datetime.strptime(self.date_trans, DATETIME_FORMAT)
        currentDate = int(date_trans.strftime("%-d"))

        #add detail pencairan
        depo_detail_obj = self.env['yudha.deposito.details']
        depo_detail_obj.create({
            'depo_id': depo_id,
            'bulan_ke': bulan_ke,
            'date_trans': date_trans,
            'jml_depo': -amount,
            'jml_actual': -amount,
            'description': description,
            'state': 'ready',
        })

        partner_obj=self.env['res.partner'].search([('id','=',yudha_obj.partner_id.id)])
        if partner_obj:
            saldo_deposito=float(partner_obj.saldo_deposito)-amount
            partner_obj.write({
                'saldo_deposito': saldo_deposito
            })
