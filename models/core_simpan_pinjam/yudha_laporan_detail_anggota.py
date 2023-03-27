# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import time

SESSION_STATES = [
        ('ready', 'Ready'),
        ('done', 'Done')
]

class yudha_laporan_detail_anggota(models.Model):
    _name = 'yudha.laporan.detail.anggota'
    _order = 'docnum desc'
    _description = "yudha LAPORAN DETAIL ANGGOTA"

   # docnum = fields.Char(string='No Validasi', default=lambda self: self.env['ir.sequence'].next_by_code('yudha.laporan.detail.anggota.1'),index=True,copy=True,required=True, readonly=True)
    docnum = fields.Char(size=100, string='No Dokument', readonly=True)
    tgl_lap = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    nm_trans = fields.Char(size=100, string='Jenis Dokument', default='Laporan Detail Anggota', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True,index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    ket = fields.Char(size=100, string='Keterangan')
    tgl_dari = fields.Date(string='Dari Tanggal',default=lambda self: time.strftime("%Y-%m-%d"), required=False)
    tgl_sampai = fields.Date(string='Sampai Tanggal',default=lambda self: time.strftime("%Y-%m-%d"), required=False)
    # jns_trans = fields.Selection([('SP', 'Simpanan Pokok'), ('SW', 'Simpanan Wajib'), ('SS', 'Simpanan Sukarela'), ('TB', 'Tabungan'), ('DP', 'Simpanan Berjangka'), ('PD', 'Pinjaman Dana'), ('PB', 'Pinjaman Barang'), ('PK', 'Pinjaman Konsumtif'), ('PSBK', 'Pinjaman Sembako'), ('PS', 'Pinjaman Syariah')], string='Jenis Transaksi',
    #                              help='Jenis Transaksi')
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi')
    lpdet_ids = fields.One2many(comodel_name='yudha.laporan.detail.anggota.details', inverse_name='lapdet_val',string='Laporan Harian')
    lpdetsimpok_ids = fields.One2many(comodel_name='yudha.laporan.detail.simpok', inverse_name="lapdetsimpok_val", string='Laporan Detail Simpanan Pokok')
    lpdetsimsuka_ids = fields.One2many(comodel_name='yudha.laporan.detail.simsuka', inverse_name="lapdetsimsuka_val", string='Laporan Detail Simpanan Pokok')
    lpdetsimwjb_ids = fields.One2many(comodel_name='yudha.laporan.detail.simwajib', inverse_name="lapdetsimwjb_val", string='Laporan Detail Simpanan Pokok')
    lpdettab_ids = fields.One2many(comodel_name='yudha.laporan.detail.tabungan', inverse_name="lapdettab_val", string='Laporan Detail Simpanan Pokok')
    lpdetdepo_ids = fields.One2many(comodel_name='yudha.laporan.detail.deposito', inverse_name="lapdetdepo_val", string='Laporan Detail Simpanan Pokok')

    lpdetpinjdana_ids = fields.One2many(comodel_name='yudha.laporan.detail.pinjdana', inverse_name="lapdetpinjdana_val", string='Laporan Detail Simpanan Pokok')

    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    @api.model
    def create(self, vals):
        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_lap', False):
            dtim = vals['tgl_lap']
        else:
            dtim = self.tgl_val
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_laporan_harian;"""
        self.env.cr.execute(myquery, )
        no_urut = self.env.cr.fetchone()[0]
        if no_urut != None or no_urut != False:
            urutan = 0
            if str(no_urut).find('/') != -1:
                pecah = no_urut.split('/')
                x = 0
                for satu in pecah:
                    if x == 2:
                        urutan = satu
                    else:
                        urutan = 0
                    x += 1
            nomerurut = int(urutan) + 1
            vals['docnum'] = 'SIMLAPDETAGT/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] = 'SIMLAPDETAGT/' + str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_detail_anggota, self).create(vals)


    
    def write(self, vals):
        if vals.get('partner_id.name', False):
            nm_agt = vals['partner_id.name']
        else:
            nm_agt = self.partner_id.name
        my_agt = self.env['res.partner'].search([('name', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_detail_anggota, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja

    def get_simpok_lengkap(self,idagt,jns, tgldari, tglsampai ):
        #mysql="""SELECT a.docnum, a.state, a.amount FROM yudha_iuran_pokok a WHERE a.partner_id=%s AND a.jns_trans=%s AND a.tgl_trans BETWEEN %s AND %s;"""
        mysql = """SELECT a.docnum, a.state, a.amount FROM yudha_iuran_pokok a WHERE a.partner_id=%s AND a.jns_trans=%s AND a.tgl_trans BETWEEN %s AND %s; """
        self.env.cr.execute(mysql, (idagt,jns,tgldari,tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil={}
        semua_hasil=[]
        if not result or result == [] :
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil={'docnum': dcn,
                       'amount': amt,
                       'state': stsa,
                }
                semua_hasil +=[hasil]
            return semua_hasil

    def get_simpok_tanggal_aja(self,tgldari, tglsampai):
        mysql="""SELECT a.docnum, a.state, a.amount FROM yudha_iuran_pokok a WHERE a.tgl_trans BETWEEN %s AND %s;"""
        self.env.cr.execute(mysql, (tgldari,tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil={}
        semua_hasil=[]
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil={'docnum': dcn,
                       'amount': amt,
                       'state': stsa,
                }
                semua_hasil +=[hasil]
            return semua_hasil

    def get_simpok_tanggal_dan_anggota(self,idagt,tgldari, tglsampai):
        mysql="""SELECT a.docnum, a.state, a.amount FROM yudha_iuran_pokok a WHERE a.partner_id=%s AND a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (idagt,tgldari,tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil={}
        semua_hasil=[]
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil={'docnum': dcn,
                       'amount': amt,
                       'state': stsa,
                }
                semua_hasil +=[hasil]
            return semua_hasil

    def get_simwjb_lengkap(self, idagt, tgldari, tglsampai, jns):
        mysql = """SELECT a.docnum, a.state, b.amount FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE b.partner_id=%s AND a.jns_trans=%s AND a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (idagt, jns, tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simwjb_tanggal_aja(self, tgldari, tglsampai):
        mysql = """SELECT a.docnum, a.state, b.amount FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE a.tgl_trans BETWEEN %s AND %s;"""
        self.env.cr.execute(mysql, (tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['jml_tab']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jml_tab': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simwjb_tanggal_dan_anggota(self, idagt, tgldari, tglsampai):
        mysql = """SELECT a.docnum, a.state, b.amount FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE b.partner_id=%s AND a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (idagt, tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simskr_lengkap(self, idagt, tgldari, tglsampai, jns):
        mysql = """SELECT a.docnum, a.state, a.amount FROM yudha_iuran_sukarela a WHERE a.partner_id=%s AND a.jns_trans=%s AND a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (idagt, jns, tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simskr_tanggal_aja(self, tgldari, tglsampai):
        mysql = """SELECT a.docnum, a.state, a.amount FROM yudha_iuran_sukarela a WHERE a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simskr_tanggal_dan_anggota(self, idagt, tgldari, tglsampai):
        mysql = """SELECT a.docnum, a.state, a.amount FROM yudha_iuran_sukarela a WHERE a.partner_id=%s AND a.tgl_trans BETWEEN %s AND %s ;"""
        self.env.cr.execute(mysql, (idagt, tgldari, tglsampai,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def masuk_details_simpok(self,ntrs,jmlnya, jmltotalnya, sts):
        res=[]
        res2=[]
        norut=0
        new_line='Y'
        for field_rekap in self.lpdetsimpok_ids:
            norut += 1
            rekap_lines = {
                'no_trans': field_rekap['no_trans'],
                'jml': field_rekap['jml'],
                'jml_total': field_rekap['jml_total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        add_line = { 'valid_id': self._origin.id,
            'no_trans': ntrs,
            'jml': jmlnya,
            'jml_total': jmltotalnya,
            'state': sts,
        }
        res += [add_line]
        res += res2
        return res

    def masuk_details_simsuka(self,ntrs,jmlnya, jmltotalnya, sts):
        res=[]
        res2=[]
        norut=0
        new_line='Y'
        for field_rekap in self.lpdetsimsuka_ids:
            norut += 1
            rekap_lines = {
                'no_trans': field_rekap['no_trans'],
                'jml': field_rekap['jml'],
                'jml_total': field_rekap['jml_total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        add_line = { 'valid_id': self._origin.id,
            'no_trans': ntrs,
            'jml': jmlnya,
            'jml_total': jmltotalnya,
            'state': sts,
        }
        res += [add_line]
        res += res2
        return res

    def masuk_details_simwajib(self,ntrs,jmlnya, jmltotalnya, sts):
        res=[]
        res2=[]
        norut=0
        new_line='Y'
        for field_rekap in self.lpdetsimwjb_ids:
            norut += 1
            rekap_lines = {
                'no_trans': field_rekap['no_trans'],
                'jml': field_rekap['jml'],
                'jml_total': field_rekap['jml_total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        add_line = { 'valid_id': self._origin.id,
            'no_trans': ntrs,
            'jml': jmlnya,
            'jml_total': jmltotalnya,
            'state': sts,
        }
        res += [add_line]
        res += res2
        return res

    def masuk_details_pinjdana(self,ntrs,jmlnya, jmltotalnya, sts):
        res=[]
        res2=[]
        norut=0
        new_line='Y'
        for field_rekap in self.lpdetpinjdana_ids:
            norut += 1
            rekap_lines = {
                'no_trans': field_rekap['no_trans'],
                'jml': field_rekap['jml'],
                'jml_total': field_rekap['jml_total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        add_line = { 'valid_id': self._origin.id,
            'no_trans': ntrs,
            'jml': jmlnya,
            'jml_total': jmltotalnya,
            'state': sts,
        }
        res += [add_line]
        res += res2
        return res

    @api.onchange('tgl_dari','tgl_sampai','jns_trans','partner_id')
    def onchange_tgl_sampai(self):
        if not self.tgl_sampai:
            return
        if not self.tgl_dari:
            return
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date1 = datetime.strptime(self.tgl_dari, DATETIME_FORMAT)
        tanggal_dari = timbang_date1.strftime('%Y-%m-%d')
        timbang_date2 = datetime.strptime(self.tgl_sampai, DATETIME_FORMAT)
        tanggal_sampai = timbang_date2.strftime('%Y-%m-%d')
        self.lpdetsimpok_ids = []
        self.lpdetsimsuka_ids = []
        self.lpdetsimwjb_ids = []
        self.lpdetpinjdana_ids = []

        if self.jns_trans == False and  self.partner_id == False:
            self.lpdet_ids = []
            myref = ''
            mystate = ''
            totamt = 0
            print('line 378','TAnggal aja')
            datasimpok = self.get_simpok_tanggal_aja(tanggal_dari,tanggal_sampai)
            if not datasimpok is None:
                print('line 330','bisa query ')
                for allsimpok in datasimpok:
                    myref = allsimpok['docnum']
                    mystate = allsimpok['state']
                    totamt += allsimpok['amount']
                    self.lpdetsimpok_ids = self.masuk_details_simpok(myref, totamt,totamt, mystate)
            myref1 = ''
            mystate1 = ''
            totamt1 = 0
            datasimwjb = self.get_simwjb_tanggal_aja(tanggal_dari,tanggal_sampai)
            if not datasimwjb is None:
                for allsimwjb in datasimwjb:
                    myref1 = allsimwjb['docnum']
                    mystate1 = allsimwjb['state']
                    totamt1 += allsimwjb['amount']
                    self.lpdetsimwjb_ids = self.masuk_details_simwajib(myref1, totamt1,totamt1, mystate1)
            myref2 = ''
            mystate2 = ''
            totamt2 = 0
            datasimskr = self.get_simskr_tanggal_aja(tanggal_dari,tanggal_sampai)
            if not datasimskr is None:
                for allsimskr in datasimskr:
                    myref2 = allsimskr['docnum']
                    mystate2 = allsimskr['state']
                    totamt2 += allsimskr['amount']
                    self.lpdetsimsuka_ids = self.masuk_details_simsuka(myref2, totamt2,totamt2, mystate2)
        elif self.partner_id and self.jns_trans == False:
            self.lpdet_ids = []
            myref = ''
            mystate = ''
            totamt = 0
            datasimpok = self.get_simpok_tanggal_dan_anggota(self.partner_id.id,tanggal_dari,tanggal_sampai)
            if not datasimpok is None:
                print('line 363', 'bisa query ')
                for allsimpok in datasimpok:
                    myref = allsimpok['docnum']
                    mystate = allsimpok['state']
                    totamt += allsimpok['amount']
                    self.lpdetsimpok_ids = self.masuk_details_simpok(myref, totamt,totamt, mystate)
            myref1 = ''
            mystate1 = ''
            totamt1 = 0
            datasimwjb = self.get_simwjb_tanggal_dan_anggota(self.partner_id.id,tanggal_dari,tanggal_sampai)
            if not datasimwjb is None:
                for allsimwjb in datasimwjb:
                    myref1 = allsimwjb['docnum']
                    mystate1 = allsimwjb['state']
                    totamt1 += allsimwjb['amount']
                    self.lpdetsimwjb_ids = self.masuk_details_simwajib(myref1, totamt1,totamt1, mystate1)
            myref2 = ''
            mystate2 = ''
            totamt2 = 0
            datasimskr = self.get_simskr_tanggal_dan_anggota(self.partner_id.id,tanggal_dari,tanggal_sampai)
            if not datasimskr is None:
                for allsimskr in datasimskr:
                    myref2 = allsimskr['docnum']
                    mystate2 = allsimskr['state']
                    totamt2 += allsimskr['amount']
                    self.lpdetsimsuka_ids = self.masuk_details_simsuka(myref2, totamt2,totamt2, mystate2)
        elif self.partner_id and self.jns_trans :
            self.lpdet_ids = []
            myref = ''
            mystate = ''
            totamt = 0
            datasimpoks = self.get_simpok_lengkap(self.partner_id.id,self.jns_trans,tanggal_dari,tanggal_sampai)
            if not datasimpoks is None:
                for allsimpok in datasimpoks:
                    myref = allsimpok['docnum']
                    mystate = allsimpok['state']
                    totamt += allsimpok['amount']
                    self.lpdetsimpok_ids = self.masuk_details_simpok(myref, totamt,totamt, mystate)
            myref1 = ''
            mystate1 = ''
            totamt1 = 0
            datasimwjb = self.get_simwjb_lengkap(self.partner_id.id,tanggal_dari,tanggal_sampai, self.jns_trans)
            if not datasimwjb is None:
                for allsimwjb in datasimwjb:
                    myref1 = allsimwjb['docnum']
                    mystate1 = allsimwjb['state']
                    totamt1 += allsimwjb['amount']
                    self.lpdetsimwjb_ids = self.masuk_details_simwajib(myref1, totamt1,totamt1, mystate1)
            myref2 = ''
            mystate2 = ''
            totamt2 = 0
            datasimskr = self.get_simskr_lengkap(self.partner_id.id,tanggal_dari,tanggal_sampai, self.jns_trans)
            if not datasimskr is None:
                for allsimskr in datasimskr:
                    myref2 = allsimskr['docnum']
                    mystate2 = allsimskr['state']
                    totamt2 += allsimskr['amount']
                    self.lpdetsimsuka_ids = self.masuk_details_simsuka(myref2, totamt2,totamt2, mystate2)

    def validate(self):
        return self.write({'state':'done'})

class yudha_laporan_detail_anggota_details(models.Model):
    _name = 'yudha.laporan.detail.anggota.details'

    lapdet_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Harian Details",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)

class yudha_laporan_detail_simpok(models.Model):
    _name = 'yudha.laporan.detail.simpok'

    lapdetsimpok_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Simpok",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)


class yudha_laporan_detail_simsuka(models.Model):
    _name = 'yudha.laporan.detail.simsuka'

    lapdetsimsuka_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Simpok",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)

class yudha_laporan_detail_simwajib(models.Model):
    _name = 'yudha.laporan.detail.simwajib'

    lapdetsimwjb_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Wajib",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)

class yudha_laporan_detail_tabungan(models.Model):
    _name = 'yudha.laporan.detail.tabungan'

    lapdettab_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Tabungan",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)

class yudha_laporan_detail_deposito(models.Model):
    _name = 'yudha.laporan.detail.deposito'

    lapdetdepo_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Deposito",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)

class yudha_laporan_detail_pinjdana(models.Model):
    _name = 'yudha.laporan.detail.pinjdana'

    lapdetpinjdana_val = fields.Many2one(comodel_name='yudha.laporan.detail.anggota', inverse_name='id', string="Laporan Details Simpok",required=False, store=True, index=True, invisible=True)
    no_trans = fields.Char(size=100, string='No. Transaksi', readonly=True)
    jml = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    jml_total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state  = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status',help='statue', readonly=True)