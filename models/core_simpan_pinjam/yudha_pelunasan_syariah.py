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
    ('draft', 'Draft'),
    ('confirm', 'Confirm'),
    ('valid', 'Validate')
]


class yudha_PelunasanSyariah(models.Model):
    _name = 'yudha.pelunasan.syariah'

    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.syariah", inverse_name='id', string="Loan Id", required=False, default=False)
    last_paydate = fields.Date(string='Tgl Angsuran Terakhir', readonly=True,default=lambda self: time.strftime("%Y-%m-%d"))
    sisa_loan = fields.Float('Sisa Pinjaman', digits=(16, 2), readonly=True, store=True, default=0)
    bunga = fields.Float('Suku Bunga pa (%)', digits=(16, 2), readonly=True, store=True, default=0)
    date_pay = fields.Date(string='Tanggal Payment', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], string='Type',default='outbound')
    sumber_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], default='CS', string='Sumber Dana',help='Sumber Dana',required=True)
    amount = fields.Float('Jumlah Pelunasan', digits=(16, 2), default=0)
    bunga_terhutang = fields.Float('Bunga Terhutang', readonly=True, digits=(16, 2), default=0)
    total_bayar = fields.Float('Jumlah Pembayaran', readonly=True, digits=(16, 2), default=0)
    description = fields.Char(size=200,default='')
    lama_cicilan = fields.Integer('Jangka Waktu (bln)', default=1)
    sisa_cicilan = fields.Integer('Sisa Angsuran', default=1)
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    @api.model
    def default_get(self, fields):
        loan_id = self._context.get('loan_ids')
        syariah_obj = self.env['yudha.peminjaman.syariah'].search([('id','=',loan_id[0])])
        rec = super(yudha_PelunasanSyariah, self).default_get(fields)
        if loan_id:
            rec.update({'loan_id': loan_id[0]})
            rec.update({'lama_cicilan': syariah_obj.lama_cicilan})
            rec.update({'sisa_cicilan': syariah_obj.sisa_cicilan})
            rec.update({'last_paydate': syariah_obj.last_paydate})
            rec.update({'sisa_loan': syariah_obj.sisa_loan})
            rec.update({'bunga': syariah_obj.bunga})
        return rec

    @api.onchange('date_pay','amount')
    def payment_onchange(self):
        day_from = datetime.strptime(self.last_paydate, "%Y-%m-%d")
        day_to = datetime.strptime(self.date_pay, "%Y-%m-%d")
        nb_of_days = (day_to - day_from).days
        # Bunga = P * i
        P = self.sisa_loan
        i = (self.bunga/365)*nb_of_days/100
        bunga_terhutang=round(P*i)
        self.bunga_terhutang=bunga_terhutang
        self.total_bayar=self.amount+bunga_terhutang

    
    def post_pelunasan(self):
        if self.date_pay == False:
            raise UserError(_('Tanggal harus diisi'))
        if self.sumber_dana == []:
            raise UserError(_('Sumber Dana harus dipilih'))
        if self.amount <= 0:
            raise UserError(_('Jumlah Pelunasan harus lebih besar dari 0'))

        day_from = datetime.strptime(self.last_paydate, "%Y-%m-%d")
        day_to = datetime.strptime(self.date_pay, "%Y-%m-%d")
        nb_of_days = (day_to - day_from).days
        # Bunga = P * i
        P = self.sisa_loan
        i = (self.bunga / 365) * nb_of_days / 100
        bunga_terhutang = round(P * i)
        total_bayar = self.amount + bunga_terhutang

        loan_id = self.loan_id.id
        last_paydate = self.last_paydate
        sisa_loan = self.sisa_loan
        bunga = self.bunga
        lama_cicilan = self.lama_cicilan
        sisa_cicilan = self.sisa_cicilan
        cicilan_ke = lama_cicilan-sisa_cicilan
        date_pay = self.date_pay
        doc_type = 'inbound'
        sumber_dana = self.sumber_dana
        amount = self.amount
        description = self.description

        lunas_obj = self.env['yudha.pelunasan.syariah']
        lunas_obj.create({
            'loan_id': loan_id,
            'last_paydate': last_paydate,
            'sisa_loan': sisa_loan,
            'bunga': bunga,
            'date_pay': date_pay,
            'doc_type': doc_type,
            'sumber_dana': sumber_dana,
            'amount': amount,
            'bunga_terhutang': bunga_terhutang,
            'total_bayar': total_bayar,
            'description': description,
            'lama_cicilan': lama_cicilan,
            'sisa_cicilan': sisa_cicilan,
            'state': 'confirm',
        })
        yudha_obj = self.env['yudha.peminjaman.syariah'].search([('id', '=', loan_id)])
        yudha_obj_detail = self.env['yudha.peminjaman.syariah.details'].search([('loan_id', '=', loan_id),('cicilan_ke','>',cicilan_ke)])
        yudha_obj_detail.unlink()
        DATETIME_FORMAT = "%Y-%m-%d"
        date_pay = datetime.strptime(self.date_pay, DATETIME_FORMAT)
        currentDate = int(date_pay.strftime("%-d"))

        if sumber_dana=='CS':
            type_pelunasan='cash'
        elif sumber_dana=='TF':
            type_pelunasan='transfer'

        #add detail pelunasan
        saldo_pinjaman=sisa_loan-amount
        pinjam_obj = self.env['yudha.peminjaman.syariah.details']
        pinjam_obj.create({
            'loan_id': loan_id,
            'cicilan_ke': 0,
            'date_pay': date_pay,
            'description': 'Pelunasan Pokok Pinjaman',
            'type_pelunasan': type_pelunasan,
            'jml_pokok': amount,
            'jml_bunga': bunga_terhutang,
            'rencana_cicilan': total_bayar,
            'saldo_pinjaman': saldo_pinjaman,
            'doc_type': 'inbound',
            'state': 'valid',
        })

        pengurang_cicilan = int(amount / yudha_obj.jml_cicilan)
        t=yudha_obj.sisa_cicilan-pengurang_cicilan
        P=yudha_obj.sisa_loan-amount
        i=bunga/12/100
        jml_cicilan = P * i / (1 - (1 + i) ** -t)
        if saldo_pinjaman>0:
            for angs in range(1, t + 1):
                # Bunga = P * i
                bunga = P * i
                pokok = jml_cicilan - bunga
                P = P - pokok
                # date_pay = self.add_one_month(date_pay)

                date_pay = date_pay + relativedelta(months=1)
                payDate = int(date_pay.strftime("%-d"))
                if payDate - currentDate < 0:
                    # cari tanggal terakhir dalam bulan payment
                    year = int(date_pay.strftime("%-Y"))
                    month = int(date_pay.strftime("%-m"))
                    lastdate = calendar.monthrange(year, month)[1]
                    if lastdate - currentDate < 0:
                        date_pay = date_pay.replace(day=lastdate)
                    else:
                        date_pay = date_pay.replace(day=currentDate)
                pinjam_obj.create({
                    'loan_id': loan_id,
                    'cicilan_ke': angs,
                    'date_pay': date_pay,
                    'description': 'Angsuran ke-' + str(angs+cicilan_ke),
                    'type_pelunasan': 'gaji',
                    'jml_pokok': round(pokok),
                    'jml_bunga': round(bunga),
                    'rencana_cicilan': round(jml_cicilan),
                    'saldo_pinjaman': round(P),
                    'doc_type': 'inbound',
                    'state': 'valid',
                })
        else:
            t=0

        jml_bayar = yudha_obj.jml_bayar + amount
        sisa_loan = yudha_obj.sisa_loan - amount
        yudha_obj.write({
            'jml_bayar': jml_bayar,
            'sisa_loan': sisa_loan,
            'sisa_cicilan': t,
            'lama_cicilan': t,
            'jml_cicilan': round(jml_cicilan),
            'jml_cicilan_view': round(jml_cicilan),
        })
        if sisa_loan == 0:
            yudha_obj.write({'state': 'done'})
        partner_obj=self.env['res.partner'].search([('id','=',yudha_obj.partner_id.id)])
        if partner_obj:
            pinj_syariah=float(partner_obj.pinj_syariah)-amount
            partner_obj.write({
                'pinj_syariah': pinj_syariah
            })
