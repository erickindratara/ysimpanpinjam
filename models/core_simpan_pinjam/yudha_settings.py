# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class yudha_settings(models.Model):
    _name = 'yudha.settings'

    code = fields.Char('code', default='settings')
    simp_pokok = fields.Float('Simpanan Pokok', digits=(16, 2), store=True, default=0)
    simp_wajib = fields.Float('Simpanan Wajib', digits=(16, 2), store=True, default=0)
    comp_usp = fields.Many2one('res.company', string='Company USP', required=True, index=True)
    comp_ho = fields.Many2one('res.company', string='Company HO', required=True, index=True)
    coa_tagihan_bulanan = fields.Many2one('account.account', string='Tagihan Bulanan Anggota', required=True, index=True)
    coa_simp_pokok = fields.Many2one('account.account', string='Simpanan Pokok', required=True, index=True)
    coa_simp_wajib = fields.Many2one('account.account', string='Simpanan Wajib', required=True, index=True)
    coa_simp_sukarela = fields.Many2one('account.account', string='Simpanan Sukarela', required=True, index=True)
    coa_tabungan_anggota = fields.Many2one('account.account', string='Tabungan Anggota', required=True, index=True)
    coa_piutang_anggota = fields.Many2one('account.account', string='Piutang Pinjaman Anggota', required=True, index=True)
    coa_jasa_pinjaman = fields.Many2one('account.account', string='Pendapatan Jasa Pinjaman', required=True, index=True)
    coa_kliring_pinjaman = fields.Many2one('account.account', string='Kliring Pinjaman', required=True, index=True, help='Digunakan sebagai default control account di module Payment pada saat pembayaran pinjaman')
    coa_kliring_tarikan = fields.Many2one('account.account', string='Kliring Setoran/Tarikan', required=True, index=True, help='Digunakan sebagai default control account di module Payment pada saat setoran/penarikan tabungan melalui transfer')
    coa_kliring_usp = fields.Many2one('account.account', string='Kliring (USP)', required=True, index=True)
    coa_kliring_ho = fields.Many2one('account.account', string='Kliring (HO)', required=True, index=True)
    coa_simp_pokok_ho = fields.Many2one('account.account', string='Simpanan Pokok', required=True, index=True)
    coa_simp_wajib_ho = fields.Many2one('account.account', string='Simpanan Wajib', required=True, index=True)
    coa_simp_sukarela_ho = fields.Many2one('account.account', string='Simpanan Sukarela', required=True, index=True)
    pot_gaji = fields.Float('Potongan Gaji (%)', digits=(16, 2), store=True, default=0)
    pot_thr = fields.Float('Potongan THR (%)', digits=(16, 2), store=True, default=0)
    pot_ik = fields.Float('Potongan IK (%)', digits=(16, 2), store=True, default=0)
    pot_jasop = fields.Float('Potongan JASOP (%)', digits=(16, 2), store=True, default=0)
    jenis_tabungan = fields.Many2one(comodel_name="yudha.master.jenis.tabungan",inverse_name='id', string="Jenis Tabungan", required=True, index=True)
    journal_id = fields.Many2one(comodel_name="account.journal",inverse_name='id', string="Journal ID", required=True, index=True)
    coa_depo_bebanjasa = fields.Many2one('account.account', string='Beban Jasa Deposito', required=True, index=True)
    coa_depo_kliring_transfer = fields.Many2one('account.account', string='Kliring Transfer', required=True, index=True)
    coa_depo_pajak = fields.Many2one('account.account', string='Pajak', required=True, index=True)
    journal_id_tab = fields.Many2one(comodel_name="account.journal",inverse_name='id', string="Journal ID", required=True, index=True)
    coa_tab_bebanjasa = fields.Many2one('account.account', string='Beban Jasa Tabungan', required=True, index=True)
    coa_tab_pajak = fields.Many2one('account.account', string='Pajak', required=True, index=True)
    coa_tab_admin = fields.Many2one('account.account', string='Biaya Administrasi', required=True, index=True)

    @api.onchange('comp_usp')
    def onchange_comp_usp(self):
        if not self.comp_usp:
            return
        sql_query = """select id,code from account_account where left(code,1) ='1' and company_id=%s order by code
                    """
        self.env.cr.execute(sql_query, (self.comp_usp.id,))
        res_id = self.env.cr.dictfetchall()
        account_list = []
        if res_id != False:
            for field in res_id:
                account_list.append(field['id'])
        sql_query = """select id,code from account_account where left(code,1) ='2' and company_id=%s order by code
                        """
        self.env.cr.execute(sql_query, (self.comp_usp.id,))
        res_id = self.env.cr.dictfetchall()
        account_list2 = []
        if res_id != False:
            for field in res_id:
                account_list2.append(field['id'])
        sql_query = """select id,code from account_account where left(code,1) ='3' and company_id=%s order by code
                            """
        self.env.cr.execute(sql_query, (self.comp_usp.id,))
        res_id = self.env.cr.dictfetchall()
        account_list3 = []
        if res_id != False:
            for field in res_id:
                account_list3.append(field['id'])

        return {'domain': {'coa_tagihan_bulanan': [('id', '=', account_list)],
                'coa_piutang_anggota': [('id', '=', account_list)],
                'coa_kliring_usp': [('id', '=', account_list)],
                'coa_tabungan_anggota': [('id', '=', account_list2)],
                'coa_simp_pokok': [('id', '=', account_list3)],
                'coa_simp_wajib': [('id', '=', account_list3)],
                'coa_simp_sukarela': [('id', '=', account_list3)]
                }}

    @api.onchange('comp_ho')
    def onchange_comp_ho(self):
        if not self.comp_ho:
            return
        sql_query = """select id,code from account_account where left(code,1) ='1' and company_id=%s order by code
                                """
        self.env.cr.execute(sql_query, (self.comp_ho.id,))
        res_id = self.env.cr.dictfetchall()
        account_ho = []
        if res_id != False:
            for field in res_id:
                account_ho.append(field['id'])
        sql_query = """select id,code from account_account where left(code,1) ='3' and company_id=%s order by code
                                        """
        self.env.cr.execute(sql_query, (self.comp_ho.id,))
        res_id = self.env.cr.dictfetchall()
        account_ho2 = []
        if res_id != False:
            for field in res_id:
                account_ho2.append(field['id'])

        return {'domain': {'coa_kliring_ho': [('id', '=', account_ho)],
                'coa_simp_pokok_ho': [('id', '=', account_ho2)],
                'coa_simp_wajib_ho': [('id', '=', account_ho2)],
                'coa_simp_sukarela_ho': [('id', '=', account_ho2)]
                }}
