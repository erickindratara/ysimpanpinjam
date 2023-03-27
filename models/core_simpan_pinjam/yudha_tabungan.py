# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import time

SESSION_STATES = [
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
]

class yudha_tabungan(models.Model):
    _name = 'yudha.tabungan'

    date = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    no_agt = fields.Char(size=100, string='No. Anggota')
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True, index=True,domain="[('active', '=', 'Y')]")
    jenis_transaksi = fields.Selection([('setoran', 'Setoran Dana'), ('tarikan', 'Tarikan Dana')],default='setoran', string='Jenis Transaksi', required=True)
    balance_awal = fields.Float('Saldo Awal', digits=(19, 2), default=0, readonly=True)
    debit = fields.Float('Jumlah Tarikan', digits=(19, 2), default=0)
    credit = fields.Float('Jumlah Setoran', digits=(19, 2), default=0)
    balance_akhir = fields.Float('Saldo Akhir', digits=(19, 2), default=0,readonly=True)
    balance = fields.Float('Balance', digits=(19, 2), default=0,)
    code_transaksi = fields.Selection([('STN', 'Setor Tunai'), ('TTN', 'Tarik Tunai'), ('BNT', 'Bunga Tabungan'), ('BND', 'Bunga Deposito'), ('PJK', 'Pajak'), ('ADM', 'Biaya Admin')], default='setoran',
                                      string='Kode Transaksi')
    keterangan = fields.Char(size=100, string='Keterangan')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])
    deposito_id = fields.Many2one(comodel_name="yudha.deposito", string="Bunga Deposito", required=False, )

    @api.onchange('no_agt')
    def onchange_no_agt(self):
        if not self.no_agt:
            return
        partner_id=self.env['res.partner'].search([('no_anggota','=',self.no_agt)])
        sql_query = """
                select sum(credit-debit) from yudha_tabungan where state='confirm' and partner_id=%s
                """
        self.env.cr.execute(sql_query, (partner_id.id,))
        self.partner_id=partner_id.id
        self.balance_awal = self.env.cr.fetchone()[0] or 0.0

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        sql_query = """
                select sum(credit-debit) from yudha_tabungan where state='confirm' and partner_id=%s
                """
        self.env.cr.execute(sql_query, (self.partner_id.id,))
        self.balance_awal = self.env.cr.fetchone()[0] or 0.0

    @api.onchange('jenis_transaksi')
    def onchange_jenis_transaksi(self):
        if self.jenis_transaksi=='setoran':
            self.code_transaksi='STN'
        else:
            self.code_transaksi='TTN'

        self.credit = 0
        self.debit=0
        self.balance_akhir=0

    @api.onchange('debit')
    def onchange_debit(self):
        self.credit=0
        self.balance_akhir=self.balance_awal-self.debit
        self.balance=self.debit*-1
        if self.balance_awal<self.debit:
            self.debit=0
            raise ValidationError(_('Saldo tidak mencukupi'))


    @api.onchange('credit')
    def onchange_credit(self):
        self.debit=0
        self.balance_akhir=self.balance_awal+self.credit
        self.balance=self.credit

    @api.model
    def create(self, vals):
        sql_query = """
                    select sum(credit-debit) from yudha_tabungan where state='confirm' and partner_id=%s
                    """
        partner_id=vals['partner_id']
        self.env.cr.execute(sql_query, (partner_id,))
        vals['balance_awal'] = self.env.cr.fetchone()[0] or 0.0
        vals['balance_akhir'] = vals['balance_awal'] + vals['credit'] - vals['debit']
        if vals['balance_awal'] == vals['balance_akhir']:
            raise ValidationError(_('Balance Awal sama dengan Balance Akhir, tidak bisa di validasi'))

        if vals['balance_awal'] < vals['debit']:
            vals['debit']=0
            raise ValidationError(_('Saldo tidak mencukupi'))

        return super(yudha_tabungan, self.with_context(mail_create_nolog=True)).create(vals)

    def write(self, vals):
        if vals.get('partner_id', False):
            partner_id = vals['partner_id']
        else:
            partner_id = self.partner_id.id

        if vals.get('debit', False):
            debit = vals['debit']
        else:
            debit = self.debit

        if vals.get('credit', False):
            credit = vals['credit']
        else:
            credit = self.credit

        sql_query = """
                    select sum(credit-debit) from yudha_tabungan where state='confirm' and partner_id=%s
                    """
        self.env.cr.execute(sql_query, (partner_id,))
        if self.state=='draft':
            vals['balance_awal'] = self.env.cr.fetchone()[0] or 0.0
            if vals['balance_awal'] < debit:
                vals['debit']=0
                raise UserError(_('Saldo tidak mencukupi'))

        vals['balance_akhir'] = self.balance_awal + credit - debit

        return super(yudha_tabungan, self).write(vals)

    def unlink(self):
        for line in self:
            if line.balance!=0:
                if line.state != 'draft':
                    raise ValidationError(_('Status Confirm tidak bisa dihapus'))
        return super(yudha_tabungan, self).unlink()

    def validate(self):
        if self.state == 'draft':
            if self.balance_awal==self.balance_akhir:
                raise ValidationError(_('Balance Awal sama dengan Balance Akhir, tidak bisa di validasi'))
            self.write({'state': 'confirm'})
            self.state = SESSION_STATES[1][0]
            #update saldo tabungan di res_partner
            res_partner_obj = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            res_partner_obj.write({'saldo_tabungan': self.balance_akhir})


