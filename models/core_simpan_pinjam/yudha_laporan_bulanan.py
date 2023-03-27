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


class yudha_laporan_bulanan(models.Model):
    _name = 'yudha.laporan.bulanan'

    # docnum = fields.Char(string='No Dokument', default=lambda self: self.env['ir.sequence'].next_by_code('yudha.laporan.bulanan.1'),index=True,copy=True,required=True, readonly=True)
    docnum = fields.Char(size=100, string='No Dokument', readonly=True)
    tahun_lap = fields.Char(string='Tahun Laporan', required=True, default='2020')
    bulan_lap = fields.Selection([('1', 'January'),
                                  ('2', 'February'),
                                  ('3','Maret'),
                                  ('4','April'),
                                  ('5','Mei'),
                                  ('6','Juni'),
                                  ('7','July'),
                                  ('8','Agustus'),
                                  ('9','September'),
                                  ('10','Oktober'),
                                  ('11','November'),
                                  ('12','Desember')],default='1', string='Bulan Laporan', help='Bulan Laporan')

    nm_trans = fields.Char(size=100, string='Jenis Dokument', default='Laporan Bulanan', readonly=True)
    ket = fields.Char(size=100, string='Keterangan')
    # lphar_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.details', inverse_name='laphar_val',string='Laporan bulanan')
    lpharsimpok_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.simpok', inverse_name='lapharsimpok_val',
                                      string='Laporan bulanan')
    lpharsuka_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.sukarela', inverse_name='lapharsuka_val',
                                    string='Laporan bulanan')
    lphartab_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.tabungan', inverse_name='laphartab_val',
                                   string='Laporan bulanan')
    lphardepo_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.deposito', inverse_name='laphardepo_val',
                                    string='Laporan bulanan')
    lpharwajib_ids = fields.One2many(comodel_name='yudha.laporan.bulanan.wajib', inverse_name='lapharwajib_val',
                                     string='Laporan bulanan')

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

        myquery = """SELECT max(docnum) FROM yudha_laporan_bulanan;"""
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
            vals['docnum'] = 'SIMLAPBUL/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['docnum'] = 'SIMLAPBUL/' + str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        return super(yudha_laporan_bulanan, self).create(vals)

    def get_simpok_lengkap(self, bulan, tahun):
        mysql = """SELECT docnum,jns_trans, state, partner_id, amount FROM yudha_iuran_pokok WHERE date_part('month',tgl_trans)=%s and date_part('year',tgl_trans)=%s;"""
        self.env.cr.execute(mysql, (bulan,tahun,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                idagt = res['partner_id']
                jtran = res['jns_trans']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jns_trans': jtran,
                         'partner_id': idagt,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simwjb_lengkap(self, bulan, tahun):
        mysql = """SELECT a.docnum,a.jns_trans, a.state,b.partner_id, b.amount FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE  date_part('month',a.tgl_trans)=%s and date_part('year',a.tgl_trans)=%s;"""
        self.env.cr.execute(mysql, (bulan,tahun,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                idagt = res['partner_id']
                jtran = res['jns_trans']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jns_trans': jtran,
                         'partner_id': idagt,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simsuka_lengkap(self, bulan,tahun):
        mysql = """SELECT docnum, jns_trans, state,partner_id, amount FROM yudha_iuran_sukarela WHERE date_part('month',tgl_trans)=%s and date_part('year',tgl_trans)=%s;"""
        self.env.cr.execute(mysql, (bulan, tahun,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                idagt = res['partner_id']
                jtran = res['jns_trans']
                amt = res['amount']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jns_trans': jtran,
                         'partner_id': idagt,
                         'amount': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simtab_lengkap(self, bulan, tahun):
        mysql = """SELECT docnum, jns_trans, state, partner_id, jml_tab FROM yudha_tabungan WHERE date_part('month',tgl_trans)=%s and date_part('year',tgl_trans)=%s;"""
        self.env.cr.execute(mysql, (bulan,tahun,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                idagt = res['partner_id']
                jtran = res['jns_trans']
                amt = res['jml_tab']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jns_trans': jtran,
                         'partner_id': idagt,
                         'jml_tab': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def get_simdepo_lengkap(self, bulan,tahun):
        mysql = """SELECT docnum, jns_trans, state, partner_id, jml_depo FROM yudha_deposito  WHERE date_part('month',tgl_trans)=%s and date_part('year' ,tgl_trans)=%s;"""
        self.env.cr.execute(mysql, (bulan,tahun,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                dcn = res['docnum']
                idagt = res['partner_id']
                jtran = res['jns_trans']
                amt = res['jml_depo']
                stsa = res['state']
                hasil = {'docnum': dcn,
                         'jns_trans': jtran,
                         'partner_id': idagt,
                         'jml_depo': amt,
                         'state': stsa,
                         }
                semua_hasil += [hasil]
            return semua_hasil

    def masuk_detail_simpok(self, ntrans, partid, jtrns, jmltrans, tot, sts):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.lpharsimpok_ids:
            norut += 1
            rekap_lines = {
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'npk': field_rekap['npk'],
                'unit_kerja': field_rekap['unit_kerja'],
                'jns_trans': field_rekap['jns_trans'],
                'no_trans': field_rekap['no_trans'],
                'jml_trans': field_rekap['jml_trans'],
                'total': field_rekap['total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        mypart = self.env['res.partner'].search([('id', '=', partid)])
        add_line = {'valid_id': self._origin.id,
                    'no_trans': ntrans,
                    'partner_id': partid,
                    'no_agt': mypart.no_anggota,
                    'npk': mypart.npk,
                    'unit_kerja': mypart.unit_kerja,
                    'jns_trans': jtrns,
                    'jml_trans': jmltrans,
                    'total': tot,
                    'state': sts,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_detail_sukarela(self, ntrans, partid, jtrns, jmltrans, tot, sts):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.lpharsuka_ids:
            norut += 1
            rekap_lines = {
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'npk': field_rekap['npk'],
                'unit_kerja': field_rekap['unit_kerja'],
                'jns_trans': field_rekap['jns_trans'],
                'no_trans': field_rekap['no_trans'],
                'jml_trans': field_rekap['jml_trans'],
                'total': field_rekap['total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        mypart = self.env['res.partner'].search([('id', '=', partid)])
        add_line = {'valid_id': self._origin.id,
                    'no_trans': ntrans,
                    'partner_id': partid,
                    'no_agt': mypart.no_anggota,
                    'npk': mypart.npk,
                    'unit_kerja': mypart.unit_kerja,
                    'jns_trans': jtrns,
                    'jml_trans': jmltrans,
                    'total': tot,
                    'state': sts,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_detail_wajib(self, ntrans, partid, jtrns, jmltrans, tot, sts):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.lpharsuka_ids:
            norut += 1
            rekap_lines = {
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'npk': field_rekap['npk'],
                'unit_kerja': field_rekap['unit_kerja'],
                'jns_trans': field_rekap['jns_trans'],
                'no_trans': field_rekap['no_trans'],
                'jml_trans': field_rekap['jml_trans'],
                'total': field_rekap['total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        mypart = self.env['res.partner'].search([('id', '=', partid)])
        add_line = {'valid_id': self._origin.id,
                    'no_trans': ntrans,
                    'partner_id': partid,
                    'no_agt': mypart.no_anggota,
                    'npk': mypart.npk,
                    'unit_kerja': mypart.unit_kerja,
                    'jns_trans': jtrns,
                    'jml_trans': jmltrans,
                    'total': tot,
                    'state': sts,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_detail_tabungan(self, ntrans, partid, jtrns, jmltrans, tot, sts):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.lphartab_ids:
            norut += 1
            rekap_lines = {
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'npk': field_rekap['npk'],
                'unit_kerja': field_rekap['unit_kerja'],
                'jns_trans': field_rekap['jns_trans'],
                'no_trans': field_rekap['no_trans'],
                'jml_trans': field_rekap['jml_trans'],
                'total': field_rekap['total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        mypart = self.env['res.partner'].search([('id', '=', partid)])
        add_line = {'valid_id': self._origin.id,
                    'no_trans': ntrans,
                    'partner_id': partid,
                    'no_agt': mypart.no_anggota,
                    'npk': mypart.npk,
                    'unit_kerja': mypart.unit_kerja,
                    'jns_trans': jtrns,
                    'jml_trans': jmltrans,
                    'total': tot,
                    'state': sts,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_detail_deposito(self, ntrans, partid, jtrns, jmltrans, tot, sts):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.lphardepo_ids:
            norut += 1
            rekap_lines = {
                'partner_id': field_rekap['partner_id'],
                'no_agt': field_rekap['no_agt'],
                'npk': field_rekap['npk'],
                'unit_kerja': field_rekap['unit_kerja'],
                'jns_trans': field_rekap['jns_trans'],
                'no_trans': field_rekap['no_trans'],
                'jml_trans': field_rekap['jml_trans'],
                'total': field_rekap['total'],
                'state': field_rekap['state'],
            }
            res2 += [rekap_lines]
        mypart = self.env['res.partner'].search([('id', '=', partid)])
        add_line = {'valid_id': self._origin.id,
                    'no_trans': ntrans,
                    'partner_id': partid,
                    'no_agt': mypart.no_anggota,
                    'npk': mypart.npk,
                    'unit_kerja': mypart.unit_kerja,
                    'jns_trans': jtrns,
                    'jml_trans': jmltrans,
                    'total': tot,
                    'state': sts,
                    }
        res += [add_line]
        res += res2
        return res

    def _get_company_id(self):
        idnya = self.env.uid
        mmsql = """SELECT b.id FROM res_users a INNER JOIN res_company b ON a.company_id=b.id where a.id=%s;"""
        self.env.cr.execute(mmsql, (idnya,))
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return

    @api.onchange('tahun_lap','bulan_lap')
    def onchange_periode_laporan(self):
        if not self.bulan_lap:
            return
        # compid = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        # mycomp = self.env['res.company'].search([('id','=',compid.company_id)])
        mycomp = self._get_company_id()

        self.lphar_ids = []
        # nosimpok = self._get_no_simpok(tanggalan)
        # print('line 96', nosimpok)
        jid = self.env['account.journal'].search(
            [('name', '=', 'Unit Simpan Pinjam'), ('company_id', '=', mycomp)], limit=1)
        datasimpok = self.get_simpok_lengkap(self.bulan_lap,self.tahun_lap)
        myref = ''
        totamt = 0
        pid = ''
        jntrs = ''
        if not datasimpok is None:
            for allsimpok in datasimpok:
                myref = allsimpok['docnum']
                mystate = allsimpok['state']
                pid = allsimpok['partner_id']
                jntrs = allsimpok['jns_trans']
                totamt += allsimpok['amount']
                self.lpharsimpok_ids = self.masuk_detail_simpok(myref, pid, jntrs, allsimpok['amount'], totamt,
                                                                allsimpok['state'])
        datasimwjb = self.get_simwjb_lengkap(self.bulan_lap,self.tahun_lap)
        myref1 = ''
        totamt1 = 0
        pid1 = ''
        jntrs1 = ''
        if not datasimwjb is None:
            for allsimwjb in datasimwjb:
                myref1 = allsimwjb['docnum']
                mystate1 = allsimwjb['state']
                pid1 = allsimwjb['partner_id']
                jntrs1 = allsimwjb['jns_trans']
                totamt1 += allsimwjb['amount']
                self.lpharwajib_ids = self.masuk_detail_wajib(myref1, pid1, jntrs1, allsimwjb['amount'], totamt1,
                                                              allsimwjb['state'])
        datasimskr = self.get_simsuka_lengkap(self.bulan_lap,self.tahun_lap)
        myref2 = ''
        totamt2 = 0
        pid2 = ''
        jntrs2 = ''
        if not datasimskr is None:
            for allsimskr in datasimskr:
                myref2 = allsimskr['docnum']
                mystate2 = allsimskr['state']
                pid2 = allsimskr['partner_id']
                jntrs2 = allsimskr['jns_trans']
                totamt2 += allsimskr['amount']
                self.lpharsuka_ids = self.masuk_detail_sukarela(myref2, pid2, jntrs2, allsimskr['amount'], totamt2,
                                                                allsimskr['state'])
        datasimtab = self.get_simtab_lengkap(self.bulan_lap,self.tahun_lap)
        myref3 = ''
        totamt3 = 0
        pid3 = ''
        jntrs3 = ''
        if not datasimtab is None:
            for allsimtab in datasimtab:
                myref3 = allsimtab['docnum']
                mystate3 = allsimtab['state']
                pid3 = allsimtab['partner_id']
                jntrs3 = allsimtab['jns_trans']
                totamt3 += allsimtab['jml_tab']
                self.lphartab_ids = self.masuk_detail_tabungan(myref3, pid3, jntrs3, allsimtab['jml_tab'], totamt3,
                                                               allsimtab['state'])
        datasimdepo = self.get_simdepo_lengkap(self.bulan_lap,self.tahun_lap)
        myref4 = ''
        totamt4 = 0
        pid4 = ''
        jntrs4 = ''
        if not datasimdepo is None:
            for allsimdepo in datasimdepo:
                myref4 = allsimdepo['docnum']
                mystate4 = allsimdepo['state']
                pid4 = allsimdepo['partner_id']
                jntrs4 = allsimdepo['jns_trans']
                totamt4 += allsimdepo['jml_depo']
                self.lphardepo_ids = self.masuk_detail_deposito(myref4, pid4, jntrs4, allsimdepo['jml_depo'], totamt4,
                                                                allsimdepo['state'])

    
    def validate(self):
        if self.state == 'done':
            raise UserError((
                                'Error!\n'
                                'Tidak dapat memvalidasi data untuk No Document %s karena sudah di Validasi ') % (
                                self.no_val))


class yudha_laporan_bulanan_simpok(models.Model):
    _name = 'yudha.laporan.bulanan.simpok'

    lapharsimpok_val = fields.Many2one(comodel_name='yudha.laporan.bulanan', inverse_name='id',
                                       string="Laporan bulanan Details", required=False, store=True, index=True,
                                       invisible=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]", readonly=True)
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi', readonly=True)
    no_trans = fields.Char(size=100, string='Nomer Transaksi', readonly=True)
    jml_trans = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status', help='statue', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_bulanan_simpok, self).create(vals)

    
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
        return super(yudha_laporan_bulanan_simpok, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja


class yudha_laporan_bulanan_wajib(models.Model):
    _name = 'yudha.laporan.bulanan.wajib'

    lapharwajib_val = fields.Many2one(comodel_name='yudha.laporan.bulanan', inverse_name='id',
                                      string="Laporan Bulanan Details", required=False, store=True, index=True,
                                      invisible=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]", readonly=True)
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi', readonly=True)
    no_trans = fields.Char(size=100, string='Nomer Transaksi', readonly=True)
    jml_trans = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status', help='statue', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_bulanan_wajib, self).create(vals)

    
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
        return super(yudha_laporan_bulanan_wajib, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja


class yudha_laporan_bulanan_sukarela(models.Model):
    _name = 'yudha.laporan.bulanan.sukarela'

    lapharsuka_val = fields.Many2one(comodel_name='yudha.laporan.bulanan', inverse_name='id',
                                     string="Laporan bulanan Details", required=False, store=True, index=True,
                                     invisible=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]", readonly=True)
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi', readonly=True)
    no_trans = fields.Char(size=100, string='Nomer Transaksi', readonly=True)
    jml_trans = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status', help='statue', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_bulanan_sukarela, self).create(vals)

    
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
        return super(yudha_laporan_bulanan_sukarela, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja


class yudha_laporan_bulanan_tabungan(models.Model):
    _name = 'yudha.laporan.bulanan.tabungan'

    laphartab_val = fields.Many2one(comodel_name='yudha.laporan.bulanan', inverse_name='id',
                                    string="Laporan bulanan Details", required=False, store=True, index=True,
                                    invisible=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]", readonly=True)
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi', readonly=True)
    no_trans = fields.Char(size=100, string='Nomer Transaksi', readonly=True)
    jml_trans = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status', help='statue', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_bulanan_tabungan, self).create(vals)

    
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
        return super(yudha_laporan_bulanan_tabungan, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja


class yudha_laporan_bulanan_deposito(models.Model):
    _name = 'yudha.laporan.bulanan.deposito'

    laphardepo_val = fields.Many2one(comodel_name='yudha.laporan.bulanan', inverse_name='id',
                                     string="Laporan bulanan Details", required=False, store=True, index=True,
                                     invisible=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]", readonly=True)
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=True)
    npk = fields.Char(size=100, string='NPK', readonly=True)
    unit_kerja = fields.Char(size=100, string='Unit Kerja', readonly=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi',
                                 help='Jenis Transaksi', readonly=True)
    no_trans = fields.Char(size=100, string='Nomer Transaksi', readonly=True)
    jml_trans = fields.Float('Jumlah', digits=(19, 2), default=0, required=True, readonly=True)
    total = fields.Float('Total', digits=(19, 2), default=0, required=True, readonly=True)
    state = fields.Selection([('ready', 'Ready'), ('done', 'Done')], string='Status', help='statue', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            nm_agt = vals['partner_id']
        else:
            nm_agt = self.partner_id.id
        my_agt = self.env['res.partner'].search([('id', '=', nm_agt)])
        if my_agt:
            vals['no_agt'] = my_agt.no_anggota
            vals['npk'] = my_agt.npk
            vals['unit_kerja'] = my_agt.unit_kerja
        return super(yudha_laporan_bulanan_deposito, self).create(vals)

    
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
        return super(yudha_laporan_bulanan_deposito, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        my_agt = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        if my_agt != False:
            self.no_agt = my_agt.no_anggota
            self.npk = my_agt.npk
            self.unit_kerja = my_agt.unit_kerja