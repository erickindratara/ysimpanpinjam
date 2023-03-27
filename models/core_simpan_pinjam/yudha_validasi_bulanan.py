# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from  odoo.exceptions import UserError
from datetime import datetime
import time

SESSION_STATES = [
        ('ready', 'Ready'),
        ('billing', 'Billing'),
        ('done', 'Done')
]

class yudha_validasi_bulanan(models.Model):
    _name = 'yudha.validasi.bulanan'
    _order = 'no_val desc'
    _description = "yudha VALIDASI BULANAN"

    confirm_by = fields.Many2one('res.users',string='Confirm By',readonly='1', default=lambda self: self.env.user)
    #no_val = fields.Char(string='No. Validasi', default=lambda self: self.env['ir.sequence'].next_by_code('yudha.validasi.bulanan.1'),index=True,copy=True,required=True,readonly=True)
    no_val = fields.Char(string='No. Validasi',readonly=True)
    jns_dok = fields.Char(string='Jenis Dokumen', default='Validasi Bulanan',index=True,copy=True,required=True, readonly=True)
    tgl_val = fields.Date(string='Tanggal Validasi', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    per_bln = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'Maret'), ('4', 'April'), ('5', 'Mei'), ('6', 'Juni'),
         ('7', 'Juli'), ('8', 'Agustus'), ('9', 'September'), ('10', 'Oktober'), ('11', 'November'),
         ('12', 'Desember')], default='1', string='Periode Bulan', help='Periode Bulan')
    pt_asal = fields.Many2one(comodel_name='yudha.asal.perusahaan', inverse_name='id', string="Asal Perusahaan",
                              required=True)
    jns_trans = fields.Selection([('TD', 'Peminjaman Dana'), ('SD', 'Pembayaran Cicilan')], string='Jenis Transaksi',default='SD',
                                 help='Jenis Transaksi')
    start_date = fields.Date(string='Tanggal Awal', default=lambda self: time.strftime("%Y-%m-%d"))
    end_date = fields.Date(string='Tanggal Akhir', default=lambda self: time.strftime("%Y-%m-%d"))
    pot_thr = fields.Boolean(string='Potongan THR')
    pot_ik = fields.Boolean(string='Potongan IK')
    pot_jasop = fields.Boolean(string='Potongan JASOP')
    wajib_ids = fields.One2many(comodel_name='yudha.validasi.simpanan.wajib',inverse_name="wajib_id",string="Angs. Wajib")
    dana_ids = fields.One2many(comodel_name='yudha.validasi.pinjaman.dana',inverse_name="dana_id",string="Angs. Dana")
    barang_ids = fields.One2many(comodel_name='yudha.validasi.pinjaman.barang',inverse_name="barang_id",string="Angs. Barang")
    konsumtif_ids = fields.One2many(comodel_name='yudha.validasi.pinjaman.konsumtif',inverse_name="konsumtif_id",string="Angs. Bunga Konsumtif")
    sembako_ids= fields.One2many(comodel_name='yudha.validasi.pinjaman.sembako',inverse_name="sembako_id",string="Angs. Sembako")
    syariah_ids= fields.One2many(comodel_name='yudha.validasi.pinjaman.syariah',inverse_name="syariah_id",string="Angs. Syariah/KPR")
    tabungan_ids = fields.One2many(comodel_name='yudha.validasi.potongan.tabungan',inverse_name="tabungan_id",string="Potongan Tabungan")
    thrikjasop_ids = fields.One2many(comodel_name='yudha.validasi.potongan.thrikjasop',inverse_name="thrikjasop_id",string="Potongan THR/IK/JAPOS")
    keterangan = fields.Char(size=100, string='Keterangan')
    move_id = fields.Many2one('account.move', string='Journal')
    move_id2 = fields.Many2one('account.move', string='Journal Kliring USP')
    move_id3 = fields.Many2one('account.move', string='Journal Kliring HO')
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



    @api.model
    def create(self, vals):
        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_val', False):
            dtim = vals['tgl_val']
        else:
            dtim = self.tgl_val
        if vals.get('pt_asal', False):
            mypt = vals['pt_asal']
        else:
            mypt = self.pt_asal
        tgl_validasi = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = tgl_validasi.strftime('%y')
        tahun2 = tgl_validasi.strftime('%Y')

        myquery = """SELECT max(no_val) FROM yudha_validasi_bulanan;"""
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
            vals['no_val'] = 'SIMVALBLN/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['no_val'] = 'SIMVALBLN/' + str(tahun2) + '/' + '1'
        vals['state'] = 'ready'

        return super(yudha_validasi_bulanan, self).create(vals)

    def unlink(self):
        if self.state == 'done':
            raise UserError((
                                'Validasi Bulanan, Error!\n'
                                'No Document %s tidak dapat dihapus, karena sudah di Validasi ') % (
                                self.no_val))
        else:
            return super(yudha_validasi_bulanan, self).unlink()

    @api.onchange('per_bln', 'jns_trans', 'pt_asal', 'start_date', 'end_date','pot_thr','pot_ik','pot_jasop')
    def onchange_per_bln(self):
        if not self.start_date or not self.end_date:
            return

        if not self.per_bln or not self.jns_trans or not self.pt_asal:
            return

        start_date=self.start_date
        end_date=self.end_date
        asal_pt=self.pt_asal.id

        DATETIME_FORMAT = "%Y-%m-%d"
        tgl_validasi = datetime.strptime(self.tgl_val, DATETIME_FORMAT)
        # bulanan = tgl_validasi.strftime('%m')
        tahun2 = tgl_validasi.strftime('%Y')
        bulanan = self.per_bln
        # compid = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        # mycomp = self.env['res.company'].search([('id','=',compid.company_id)])
        mycomp = self._get_company_id()
        # nosimpok = self._get_no_simpok(tanggalan)
        # print('line 96', nosimpok)
        jid = self.env['account.journal'].search(
            [('name', '=', 'Unit Simpan Pinjam'), ('company_id', '=', mycomp)], limit=1)

        # Change by Agus
        # --> Perhitungan Simpanan Wajib
        # --> Perhitungan Potongan Tabungan
        # --> Perhitungan Potongan Pinjaman Dana
        # --> Perhitungan Potongan Pinjaman Barang
        # --> Perhitungan Potongan Pinjaman Konsumtif
        # --> Perhitungan Potongan Pinjaman Sembako
        # --> Perhitungan Potongan Pinjaman Syariah
        # --> Perhitungan Potongan THR/IK/JAPOS

        # --> Perhitungan Simpanan Wajib
        #self.generate_simpanan_wajib(self.jns_trans, self.pt_asal.id)
        self.wajib_ids = []
        self.wajib_ids = self.get_simpanan_wajib(self.jns_trans, self.pt_asal.id)

        # --> Perhitungan Potongan Tabungan
        # self.generate_potongan_gaji(self.jns_trans)
        self.tabungan_ids = []
        self.tabungan_ids = self.get_potongan_tabungan(self.pt_asal.id)

        # # --> Perhitungan Potongan Pinjaman Dana
        self.dana_ids = []
        self.dana_ids = self.get_pinjamdana(self.jns_trans, tahun2, bulanan)

        # # --> Perhitungan Potongan Pinjaman Barang
        self.barang_ids = []
        self.barang_ids = self.get_pinjambarang(self.jns_trans, tahun2, bulanan)

        # # --> Perhitungan Potongan Pinjaman Konsumtif
        self.konsumtif_ids = []
        self.konsumtif_ids = self.get_pinjamkonsumtif(self.jns_trans, tahun2, bulanan)

        # # --> Perhitungan Potongan Pinjaman Sembako
        self.sembako_ids = []
        self.sembako_ids = self._get_summary_sembako(start_date,end_date,asal_pt)

        # # --> Perhitungan Potongan Pinjaman Syariah
        self.syariah_ids = []
        self.syariah_ids = self.get_pinjamsyariah(self.jns_trans, tahun2, bulanan)

        # # --> Perhitungan Potongan THR/IK/JAPOS
        if self.pot_thr or self.pot_ik or self.pot_jasop:
            self.thrikjasop_ids = []
            self.thrikjasop_ids = self.get_potongan_thrikjasop(self.pot_thr, self.pot_ik, self.pot_jasop)
        else:
            self.thrikjasop_ids = []

    def get_potongan_tabungan(self,asal_pt):
        data_anggota = self.env['res.partner'].search(['&', ('asal_pt', '=', asal_pt), ('category_id', '=', 'Anggota'), ('pot_tab', '>', '0')])
        if data_anggota:
            res = []
            for field_rekap in data_anggota:
                rekap_lines = {
                    'tabungan_id': self._origin.id,
                    'partner_id': field_rekap['id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': field_rekap['pot_tab'],
                    'realisasi': field_rekap['pot_tab'],
                    'state': 'ready',
                }
                res += [rekap_lines]
            return res

    def get_simpanan_wajib(self,jns_trans,asal_pt):
        data_anggota = self.env['res.partner'].search([('asal_pt', '=', asal_pt), ('category_id', '=', 'Anggota')])
        res = []
        if data_anggota:
            settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
            simp_wajib = settings_obj.simp_wajib
            for field_rekap in data_anggota:
                rekap_lines = {
                    'wajib_id': self._origin.id,
                    'jns_simpanan': 'wajib',
                    'partner_id': field_rekap['id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': simp_wajib,
                    'realisasi': simp_wajib,
                    'state': 'ready',
                }
                res += [rekap_lines]
        #cek iuran pokok yang dari potong gaji
        sql_query="""select a.partner_id,b.no_anggota,b.npk,b.unit_kerja,b.asal_pt,a.amount from yudha_iuran_pokok a inner join res_partner b on a.partner_id=b.id 
            where a.jns_trans='SD' and a.asal_dana='PG' and a.tgl_trans between %s and %s and b.asal_pt=%s;
            """
        self.env.cr.execute(sql_query, (self.start_date, self.end_date, self.pt_asal.id,))
        result = self.env.cr.dictfetchall()
        if result:
            for field_rekap in result:
                rekap_lines = {
                    'wajib_id': self._origin.id,
                    'jns_simpanan': 'pokok',
                    'partner_id': field_rekap['partner_id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': field_rekap['amount'],
                    'realisasi': field_rekap['amount'],
                    'state': 'ready',
                }
                res += [rekap_lines]

        #cek iuran sukarela yang dari potong gaji
        sql_query = """select a.partner_id,b.no_anggota,b.npk,b.unit_kerja,b.asal_pt,a.amount from yudha_iuran_sukarela a inner join res_partner b on a.partner_id=b.id 
                    where a.jns_trans='SD' and a.asal_dana='PG' and a.tgl_trans between %s and %s and b.asal_pt=%s;
                    """
        self.env.cr.execute(sql_query, (self.start_date, self.end_date, self.pt_asal.id,))
        result = self.env.cr.dictfetchall()
        if result:
            for field_rekap in result:
                rekap_lines = {
                    'wajib_id': self._origin.id,
                    'jns_simpanan': 'rela',
                    'partner_id': field_rekap['partner_id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': field_rekap['amount'],
                    'realisasi': field_rekap['amount'],
                    'state': 'ready',
                }
                res += [rekap_lines]

        return res

    def get_potongan_thrikjasop(self,thr,ik,jasop):
        if thr==True and ik==True and jasop==True:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,a.pot_thr,a.pot_ik,a.pot_jasop
                from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_ik+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                union
                select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,a.pot_thr,a.pot_ik,a.pot_jasop
                from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_ik+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                """
        elif thr == True and ik == True and jasop == False:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,a.pot_thr,a.pot_ik,0 as pot_jasop
                from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_ik>0 and a.state='paid' and b.asal_pt=%s
                union
                select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,a.pot_thr,a.pot_ik,0 as pot_jasop
                from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_ik>0 and a.state='paid' and b.asal_pt=%s
                """
        elif thr == True and ik == False and jasop == False:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,a.pot_thr,0 as pot_ik,0 as pot_jasop
                from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_thr>0 and a.state='paid' and b.asal_pt=%s
                union
                select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,a.pot_thr,0 as pot_ik,0 as pot_jasop
                from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_thr>0 and a.state='paid' and b.asal_pt=%s
                """
        elif thr == False and ik == True and jasop == False:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,0 as pot_thr,a.pot_ik,0 as pot_jasop
                    from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_ik>0 and a.state='paid' and b.asal_pt=%s
                    union
                    select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,0 as pot_thr,a.pot_ik,0 as pot_jasop
                    from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_ik>0 and a.state='paid' and b.asal_pt=%s
                    """
        elif thr == False and ik == True and jasop == True:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,0 as pot_thr,a.pot_ik,a.pot_jasop
                    from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_ik+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                    union
                    select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,0 as pot_thr,a.pot_ik,a.pot_jasop
                    from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_ik+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                    """
        elif thr == True and ik == False and jasop == True:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,a.pot_thr,0 as pot_ik,a.pot_jasop
                    from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                    union
                    select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,a.pot_thr,0 as pot_ik,a.pot_jasop
                    from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_thr+a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                    """
        elif thr == False and ik == False and jasop == True:
            mysql = """select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'konsumtif' as jenis_pinjaman,'persen' as type_potongan ,0  as pot_thr,0 as pot_ik,a.pot_jasop
                from yudha_peminjaman_konsumtif a inner join res_partner b on a.partner_id=b.id where a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                union
                select a.docnum,a.id,a.partner_id,a.no_agt,a.npk,a.unit_kerja,b.asal_pt,'syariah' as jenis_pinjaman,'amount' as type_potongan ,0 as pot_thr,0 as pot_ik,a.pot_jasop
                from yudha_peminjaman_syariah a inner join res_partner b on a.partner_id=b.id where a.pot_jasop>0 and a.state='paid' and b.asal_pt=%s
                """
        elif thr == False and ik == False and jasop == False:
            return

        self.env.cr.execute(mysql, (self.pt_asal.id, self.pt_asal.id,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil = []
            for field_rekap in result:
                rekap_lines = {
                    'thrikjapos_id': self._origin.id,
                    'partner_id': field_rekap['partner_id'],
                    'docnum': field_rekap['docnum'],
                    'no_anggota': field_rekap['no_agt'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'jenis_pinjaman': field_rekap['jenis_pinjaman'],
                    'type_potongan': field_rekap['type_potongan'],
                    'pot_thr': field_rekap['pot_thr'],
                    'pot_ik': field_rekap['pot_ik'],
                    'pot_jasop': field_rekap['pot_jasop'],
                    'real_thr': 0,
                    'real_ik': 0,
                    'real_jasop': 0,
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def _get_summary_sembako(self,start_date,end_date,asal_pt):
        sql_query = """select a.partner_id,c.no_anggota,c.npk,c.unit_kerja,c.asal_pt,sum(a.amount) as amount
                from account_bank_statement_line a inner join account_journal b on a.journal_id=b.id 
                inner join res_partner c on a.partner_id=c.id
                where b.name='Kredit Anggota' and a.date between %s and %s and c.asal_pt=%s
                group by a.partner_id,c.no_anggota,c.npk,c.unit_kerja,c.asal_pt order by a.partner_id;
                """
        self.env.cr.execute(sql_query, (start_date, end_date, asal_pt,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil = []
            for field_rekap in result:
                rekap_lines = {
                    'sembako_id': self._origin.id,
                    'partner_id': field_rekap['partner_id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'amount': field_rekap['amount'],
                    'realisasi': field_rekap['amount'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def get_pinjamsembako(self,jnst,thun,bln):
        #subject dirubah --> ambil langsung dari penjualan POS berdasarkan Member
        if not jnst:
            return
        mysql = """select b.docnum,b.no_accmove, b.state,a.rencana_cicilan, b. partner_id,
            c.no_rek_agt,c.nm_bank,c.atas_nama from yudha_peminjaman_dana_details a inner join yudha_peminjaman_dana b 
            on a.loan_id=b.id inner join res_partner c on b.partner_id=c.id where b.state='paid' AND a.doc_type='inbound'
            AND c.asal_pt=%s AND date_part('year',a.date_pay)=%s AND date_part('month',a.date_pay)=%s;
            """
        self.env.cr.execute(mysql, (self.pt_asal.id, thun, bln,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for field_rekap in result:
                rekap_lines = {
                    'dana_id': self._origin.id,
                    'no_trans': field_rekap['docnum'],
                    'no_accmove': '',
                    'amount': field_rekap['rencana_cicilan'],
                    'realisasi': field_rekap['rencana_cicilan'],
                    'jns_trans': 'SD',
                    'partner_id': field_rekap['partner_id'],
                    'no_rek_agt   ': field_rekap['no_rek_agt'],
                    'nm_bank': field_rekap['nm_bank'],
                    'atas_nama': field_rekap['atas_nama'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def get_pinjamdana(self,jnst,thun,bln):
        if not jnst:
            return
        sql_query="""select b.partner_id,a.id as detail_id,c.no_anggota,c.npk,c.unit_kerja,c.asal_pt,
            a.jml_pokok,a.jml_bunga,
            a.rencana_cicilan as amount from yudha_peminjaman_dana_details a inner join yudha_peminjaman_dana b 
            on a.loan_id=b.id inner join res_partner c on b.partner_id=c.id where b.state='paid' AND a.doc_type='inbound'
            AND c.asal_pt=%s AND date_part('year',a.date_pay)=%s AND date_part('month',a.date_pay)=%s;
            """
        self.env.cr.execute(sql_query, (self.pt_asal.id, thun, bln,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            semua_hasil = []
            for field_rekap in result:
                rekap_lines = {
                    'dana_id': self._origin.id,
                    'partner_id': field_rekap['partner_id'],
                    'detail_id': field_rekap['detail_id'],
                    'no_anggota': field_rekap['no_anggota'],
                    'npk': field_rekap['npk'],
                    'unit_kerja': field_rekap['unit_kerja'],
                    'asal_pt': field_rekap['asal_pt'],
                    'jml_pokok': field_rekap['jml_pokok'],
                    'jml_bunga': field_rekap['jml_bunga'],
                    'amount': field_rekap['amount'],
                    'realisasi': field_rekap['amount'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def get_pinjambarang(self,jnst,thun,bln):
        if not jnst:
            return
        mysql = """select b.docnum,a.id as detail_id,b.no_accmove, b.state,a.jml_pokok,a.jml_bunga,
            a.rencana_cicilan, b. partner_id,
            c.no_rek_agt,c.nm_bank,c.atas_nama from yudha_peminjaman_barang_details a inner join yudha_peminjaman_barang b 
            on a.loan_id=b.id inner join res_partner c on b.partner_id=c.id where b.state='paid' AND a.doc_type='inbound'
            AND c.asal_pt=%s AND date_part('year',a.date_pay)=%s AND date_part('month',a.date_pay)=%s;
            """
        self.env.cr.execute(mysql, (self.pt_asal.id, thun, bln,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for field_rekap in result:
                rekap_lines = {
                    'barang_id': self._origin.id,
                    'no_trans': field_rekap['docnum'],
                    'detail_id': field_rekap['detail_id'],
                    'no_accmove': '',
                    'jml_pokok': field_rekap['jml_pokok'],
                    'jml_bunga': field_rekap['jml_bunga'],
                    'amount': field_rekap['rencana_cicilan'],
                    'realisasi': field_rekap['rencana_cicilan'],
                    'jns_trans': 'SD',
                    'partner_id': field_rekap['partner_id'],
                    'no_rek_agt   ': field_rekap['no_rek_agt'],
                    'nm_bank': field_rekap['nm_bank'],
                    'atas_nama': field_rekap['atas_nama'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def get_pinjamkonsumtif(self,jnst, thun, bln):
        if not jnst:
            return
        mysql = """select b.docnum,b.id,a.id as detail_id,b.no_accmove, b.state,a.rencana_cicilan, b. partner_id,
            c.no_rek_agt,c.nm_bank,c.atas_nama from yudha_peminjaman_konsumtif_details a inner join yudha_peminjaman_konsumtif b 
            on a.loan_id=b.id inner join res_partner c on b.partner_id=c.id where b.state='paid' AND a.doc_type='inbound'
            AND c.asal_pt=%s AND date_part('year',a.date_pay)=%s AND date_part('month',a.date_pay)=%s;
            """
        self.env.cr.execute(mysql, (self.pt_asal.id, thun, bln,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for field_rekap in result:
                rekap_lines = {
                    'konsumtif_id': self._origin.id,
                    'loan_id': field_rekap['id'],
                    'detail_id': field_rekap['detail_id'],
                    'no_trans': field_rekap['docnum'],
                    'no_accmove': '',
                    'amount': field_rekap['rencana_cicilan'],
                    'realisasi': field_rekap['rencana_cicilan'],
                    'jns_trans': 'SD',
                    'partner_id': field_rekap['partner_id'],
                    'no_rek_agt   ': field_rekap['no_rek_agt'],
                    'nm_bank': field_rekap['nm_bank'],
                    'atas_nama': field_rekap['atas_nama'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def get_pinjamsyariah(self,jnst, thun, bln):
        if not jnst:
            return
        mysql = """select b.docnum,b.id,a.id as detail_id,b.no_accmove, b.state,a.rencana_cicilan, b. partner_id,
            c.no_rek_agt,c.nm_bank,c.atas_nama from yudha_peminjaman_syariah_details a inner join yudha_peminjaman_syariah b 
            on a.loan_id=b.id inner join res_partner c on b.partner_id=c.id where b.state='paid' AND a.doc_type='inbound'
            AND c.asal_pt=%s AND date_part('year',a.date_pay)=%s AND date_part('month',a.date_pay)=%s;
            """
        self.env.cr.execute(mysql, (self.pt_asal.id, thun, bln,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for field_rekap in result:
                rekap_lines = {
                    'syariah_id': self._origin.id,
                    'loan_id': field_rekap['id'],
                    'detail_id': field_rekap['detail_id'],
                    'no_trans': field_rekap['docnum'],
                    'no_accmove': '',
                    'amount': field_rekap['rencana_cicilan'],
                    'realisasi': field_rekap['rencana_cicilan'],
                    'jns_trans': 'SD',
                    'partner_id': field_rekap['partner_id'],
                    'no_rek_agt   ': field_rekap['no_rek_agt'],
                    'nm_bank': field_rekap['nm_bank'],
                    'atas_nama': field_rekap['atas_nama'],
                    'state': 'ready',
                }
                semua_hasil += [rekap_lines]
            return semua_hasil

    def _update_kontak_pinjam(self,dcn, nmove):
        if str(dcn).find('SIMWJB') != -1:
            mysql = """SELECT b.partner_id, b.amount FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpok = res_partner_obj.iuran_pokok + res['amount']
                        res_partner_obj.write({'iuran_wajib': totpok})
                    else:
                        res_partner_obj.write({'iuran_wajib': res['amount']})
                res_dtl = self.env['yudha.iuran.wajib'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMSBK') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_sembako a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsembako = res_partner_obj.pinj_sembako + res['jml_pinjam']
                        res_partner_obj.write({'pinj_semabko': totsembako})
                    else:
                        res_partner_obj.write({'pinj_sembako': res['jml_pinjam']})
                res_dtl = self.env['yudha.pinjaman.sembako'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMBRG') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_barang a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpnjbrg = res_partner_obj.pinj_barang + res['jml_pinjam']
                        res_partner_obj.write({'pinj_barang': totpnjbrg})
                    else:
                        res_partner_obj.write({'pinj_barang': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.barang'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMKONS') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_konsumtif a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpnjkons = res_partner_obj.pinj_konsumtif + res['jml_pinjam']
                        res_partner_obj.write({'pinj_komsumtif': totpnjkons})
                    else:
                        res_partner_obj.write({'pinj_sembako': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.konsumtif'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMSYRAH') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_syariah a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            totdepo = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpnjsyariah = res_partner_obj.pinj_syariah + res['jml_pinjam']
                        res_partner_obj.write({'pinj_syariah': totpnjsyariah})
                    else:
                        res_partner_obj.write({'pinj_syariah': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.syariah'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMDANA') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_dana a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            totdepo = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpnjdana = res_partner_obj.pinj_dana + res['jml_pinjam']
                        res_partner_obj.write({'pinj_dana': totpnjdana})
                    else:
                        res_partner_obj.write({'pinj_dana': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.dana'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })

    def _update_kontak_bayar(self, dcn, nmove):
        if str(dcn).find('SIMWJB') != -1:
            mysql = """SELECT b.partner_id, b.amount, FROM yudha_iuran_wajib a INNER JOIN yudha_iuran_wajib_details b ON a.id=b.iuranwjb_val WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totwjb = res_partner_obj.iuran_pokok - res['amount']
                        res_partner_obj.write({'iuran_wajib': totwjb})
                    else:
                        res_partner_obj.write({'iuran_wajib': res['amount']})
                res_dtl = self.env['yudha.iuran.wajib'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})
        elif str(dcn).find('SIMSBK') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_sembako a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsbk = res_partner_obj.pinj_sembako - res['jml_pinjam']
                        res_partner_obj.write({'pinj_sembako': totsbk})
                    else:
                        res_partner_obj.write({'pinj_sembako': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.sembako'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})
        elif str(dcn).find('SIMBRG') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjaman FROM yudha_peminjaman_barang a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totbrg = res_partner_obj.pinj_barang - res['jml_pinjaman']
                        res_partner_obj.write({'pinj_barang': totbrg})
                    else:
                        res_partner_obj.write({'pinj_barang': res['amount']})
                res_dtl = self.env['yudha.peminjaman.barang'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})
        elif str(dcn).find('SIMKONS') != -1:
            mysql = """SELECT a.partner_id, b.jml_pinjam FROM yudha_peminjaman_konsumtif a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totkons = res_partner_obj.pinj_konsumtif - res['jml_pinjam']
                        res_partner_obj.write({'pinj_konsumtif': totkons})
                    else:
                        res_partner_obj.write({'pinj_konsumtif': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.konsumtif'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})
        elif str(dcn).find('SIMSYRAH') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_syariah a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            totdepo = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsyariah = res_partner_obj.pinj_syariah - res['jml_pinjam']
                        res_partner_obj.write({'pinj_syariah': totsyariah})
                    else:
                        res_partner_obj.write({'pinj_syariah': res['jml_pinjam']})
                res_dtl = self.env['yudha.peminjaman.syariah'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})
        elif str(dcn).find('SIMDANA') != -1:
            mysql = """SELECT a.partner_id, a.jml_pinjam FROM yudha_peminjaman_dana a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn,))
            result = self.env.cr.dictfetchall()
            totdepo = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totdana = res_partner_obj.pinj_dana - res['jml_depo']
                        res_partner_obj.write({'pinj_dana': totdana})
                    else:
                        res_partner_obj.write({'pinj_dana': res['jml_depo']})
                res_dtl = self.env['yudha.peminjaman.dana'].search([('docnum', '=', dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done'})

    def _get_company_id(self):
        idnya = self.env.uid
        mmsql="""SELECT b.id FROM res_users a INNER JOIN res_company b ON a.company_id=b.id where a.id=%s;"""
        self.env.cr.execute(mmsql, (idnya,))
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return

    def get_last_journal(self):
        #mmsql = """SELECT count(name) FROM account_move;"""
        mmsql="""SELECT max(id) FROM account_move;"""
        self.env.cr.execute(mmsql,)
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return 0

    def Autonumber_Simwajib(self):
        if self.tgl_val==False:
            return
        DATETIME_FORMAT = "%Y-%m-%d"
        dtim = self.tgl_val
        tgl_validasi = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun2 = tgl_validasi.strftime('%Y')

        myquery = """SELECT max(docnum) FROM yudha_iuran_wajib;"""
        self.env.cr.execute(myquery,)
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
            nourutnya = 'SIMWJB/' + str(tahun2) + '/' + str(nomerurut)
        else:
            nourutnya ='SIMWJB/'+ str(tahun2) + '/' + '1'

        return nourutnya

    
    def billing_confirm(self):
        if self.state == 'done':
            raise UserError(('Error!\n'
                'No Document %s sudah di Validasi ') % (
                self.no_val))
        wajib_obj = self.env['yudha.validasi.simpanan.wajib'].search([('wajib_id', '=', self.id)])
        wajib_obj.write({'state': 'billing'})

        tabungan_obj = self.env['yudha.validasi.potongan.tabungan'].search([('tabungan_id', '=', self.id)])
        tabungan_obj.write({'state': 'billing'})

        dana_obj=self.env['yudha.validasi.pinjaman.dana'].search([('dana_id','=',self.id)])
        dana_obj.write({'state':'billing'})

        barang_obj = self.env['yudha.validasi.pinjaman.barang'].search([('barang_id', '=', self.id)])
        barang_obj.write({'state': 'billing'})

        konsumtif_obj = self.env['yudha.validasi.pinjaman.konsumtif'].search([('konsumtif_id', '=', self.id)])
        konsumtif_obj.write({'state': 'billing'})

        sembako_obj = self.env['yudha.validasi.pinjaman.sembako'].search([('sembako_id', '=', self.id)])
        sembako_obj.write({'state': 'billing'})

        syariah_obj = self.env['yudha.validasi.pinjaman.syariah'].search([('syariah_id', '=', self.id)])
        syariah_obj.write({'state': 'billing'})

        thrikjasop_obj = self.env['yudha.validasi.potongan.thrikjasop'].search([('thrikjasop_id', '=', self.id)])
        thrikjasop_obj.write({'state': 'billing'})

        self.write({'state':'billing'})

    
    def validate(self):
        if self.state == 'done':
            raise UserError(('Error!\n''No Document %s sudah di Validasi ') % (self.no_val))

        #1. Validasi Bulanan
        mycomp = self._get_company_id()
        tahun = datetime.now().year
        lstjr = self.get_last_journal()
        counter = str(lstjr + 1)
        nama_account = '%s/%s/%s' % ('KOPKARTRNS', tahun, counter)
        nama_account2=self.env['ir.sequence'].next_by_code('account.journal')
        journal_id = self.env['account.journal'].search([('name', '=', 'Unit Simpan Pinjam'), ('company_id', '=', mycomp)], limit=1)
        acc_analytic = self.env['account.analytic.account'].search(['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', mycomp)],limit=1)
        simpanan_wajib=0
        simpanan_pokok=0
        simpanan_sukarela=0
        potongan_tabungan=0
        angsuran_dana=0
        angsuran_pokok_dana=0
        angsuran_jasa_dana=0
        angsuran_barang=0
        angsuran_pokok_barang=0
        angsuran_jasa_barang=0
        angsuran_konsumtif=0
        angsuran_pokok_konsumtif=0
        angsuran_jasa_konsumtif=0
        angsuran_sembako=0
        angsuran_syariah=0
        angsuran_pokok_syariah=0
        angsuran_jasa_syariah=0

        for line in self.wajib_ids:
            if line.jns_simpanan == 'wajib':
                simpanan_wajib += line.realisasi
            elif line.jns_simpanan == 'pokok':
                simpanan_pokok += line.realisasi
            elif line.jns_simpanan == 'rela':
                simpanan_sukarela += line.realisasi
        for line in self.tabungan_ids:
            potongan_tabungan += line.realisasi
        for line in self.dana_ids:
            angsuran_dana += line.realisasi
            angsuran_pokok_dana += line.realisasi-line.jml_bunga
            angsuran_jasa_dana += line.jml_bunga
        for line in self.barang_ids:
            angsuran_barang += line.realisasi
            angsuran_pokok_barang += line.realisasi-line.jml_bunga
            angsuran_jasa_barang += line.jml_bunga
        for line in self.konsumtif_ids:
            angsuran_konsumtif += line.realisasi
            angsuran_jasa_konsumtif += line.realisasi
        for line in self.sembako_ids:
            angsuran_sembako += line.realisasi
        for line in self.syariah_ids:
            angsuran_syariah += line.realisasi
        for line in self.thrikjasop_ids:
            if line.jenis_pinjaman=='konsumtif':
                angsuran_konsumtif += line.real_thr+line.real_ik+line.real_jasop
                angsuran_pokok_konsumtif += line.real_thr+line.real_ik+line.real_jasop
            elif line.jenis_pinjaman=='syariah':
                angsuran_syariah += line.real_thr+line.real_ik+line.real_jasop
        acc_header = {}
        acc_detail = []

        acc_header = {'date': fields.datetime.now(),
                      'journal_id': journal_id.id,
                      'company_id': mycomp,
                      'ref': 'Penerimaan Pembayaran Pinjaman',
                      'name': nama_account}
        settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
        if simpanan_wajib>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Simpanan Wajib',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_wajib,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_wajib.id,
                        'name': 'Simpanan Wajib',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_wajib}
            acc_detail.append((0, 0, acc_line))
        if simpanan_pokok>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Simpanan Pokok',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_pokok,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_pokok.id,
                        'name': 'Simpanan Pokok',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_pokok}
            acc_detail.append((0, 0, acc_line))
        if simpanan_sukarela>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Simpanan Sukarela',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_sukarela,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_sukarela.id,
                        'name': 'Simpanan Pokok',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_sukarela}
            acc_detail.append((0, 0, acc_line))
        if potongan_tabungan>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Potongan Tabungan',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': potongan_tabungan,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_tabungan_anggota.id,
                        'name': 'Potongan Tabungan',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': potongan_tabungan}
            acc_detail.append((0, 0, acc_line))
        if angsuran_dana>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Angsuran Pinjaman Dana',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': angsuran_dana,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_piutang_anggota.id,
                        'name': 'Angsuran Pokok Pinjaman Dana',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_pokok_dana}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_jasa_pinjaman.id,
                        'name': 'Jasa Pinjaman Dana',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_jasa_dana}
            acc_detail.append((0, 0, acc_line))
        if angsuran_barang>0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Angsuran Pinjaman Barang',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': angsuran_barang,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_piutang_anggota.id,
                        'name': 'Angsuran Pokok Pinjaman Barang',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_pokok_barang}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_jasa_pinjaman.id,
                        'name': 'Jasa Pinjaman Barang',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_jasa_barang}
            acc_detail.append((0, 0, acc_line))
        if angsuran_konsumtif > 0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Angsuran Pinjaman Konsumtif',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': angsuran_konsumtif,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            if angsuran_pokok_konsumtif > 0:
                acc_line = {'account_id': settings_obj.coa_piutang_anggota.id,
                            'name': 'Angsuran Pokok Pinjaman Konsumtif',
                            'analytic_account_id': acc_analytic.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': angsuran_pokok_konsumtif}
                acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_jasa_pinjaman.id,
                        'name': 'Jasa Pinjaman Konsumtif',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_jasa_konsumtif}
            acc_detail.append((0, 0, acc_line))
        if angsuran_sembako > 0:
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Angsuran Pinjaman Sembako',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': angsuran_sembako,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_piutang_anggota.id,
                        'name': 'Angsuran Pinjaman Sembako',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': angsuran_sembako}
            acc_detail.append((0, 0, acc_line))
        # Pinjaman Syariah
        if angsuran_syariah > 0:
            pokok=0
            bunga=0
            for syariah in self.syariah_ids:
                syariah_details_obj = self.env['yudha.peminjaman.syariah.details'].search(
                    [('id', '=', syariah.detail_id.id)])
                if syariah_details_obj:
                    # Update Detail
                    total_cicilan = syariah_details_obj.cicilan_bulanan
                    P = self.env['yudha.peminjaman.syariah'].search([('id', '=', syariah.loan_id.id)]).jml_pinjam
                    P_bln = P
                    sql_query = """select pot_thr,pot_ik,pot_jasop,real_thr,real_ik,real_jasop from yudha_validasi_potongan_thrikjasop where
                        jenis_pinjaman='syariah' and docnum=%s and thrikjasop_id=%s;
                        """
                    self.env.cr.execute(sql_query, (syariah_details_obj.loan_id.docnum, self.id,))
                    result = self.env.cr.dictfetchall()
                    pot_thr = 0
                    pot_ik = 0
                    pot_jasop = 0
                    real_thr = 0
                    real_ik = 0
                    real_jasop = 0

                    if result:
                        for kpr in result:
                            pot_thr = kpr['pot_thr']
                            pot_ik = kpr['pot_ik']
                            pot_jasop = kpr['pot_jasop']
                            real_thr = kpr['real_thr']
                            real_ik = kpr['real_ik']
                            real_jasop = kpr['real_jasop']
                    # hitung pokok dan bunga
                    angs = syariah_details_obj.cicilan_ke
                    thn = int(1 + ((angs - 1) / 12))
                    beban_bunga = self.env['yudha.peminjaman.syariah.summary'].search(
                        [('loan_id','=',syariah.loan_id.id),('tahun_ke', '=', thn)]).cicilan_bunga
                    beban_bunga_bln = beban_bunga / 12
                    hutang_bunga_bln = 0
                    details_obj = self.env['yudha.peminjaman.syariah.details'].search(
                        [('loan_id', '=', syariah.loan_id.id), ('cicilan_ke', '<=', angs),
                         ('jml_cicilan', '>', 0)])

                    if details_obj:
                        total_beban_bunga = beban_bunga_bln + hutang_bunga_bln
                        for line in details_obj:
                            if line.jml_cicilan < total_beban_bunga:
                                hutang_bunga_bln += beban_bunga_bln - line.jml_cicilan
                            else:
                                hutang_bunga_bln = 0
                            P_bln = P_bln - line.jml_pokok

                    total_beban_bunga = beban_bunga_bln + hutang_bunga_bln
                    total_cicilan = real_ik + real_thr + real_jasop + syariah_details_obj.cicilan_bulanan
                    if total_cicilan < total_beban_bunga:
                        bunga = total_cicilan
                        pokok = 0
                    else:
                        bunga = total_beban_bunga
                        pokok = total_cicilan - total_beban_bunga
                    P_bln = P_bln - pokok
                    syariah_details_obj.write({'cicilan_triwulan': real_ik,
                                               'cicilan_tahunan': real_thr + real_jasop,
                                               'rencana_cicilan': pot_ik + pot_thr + pot_jasop + syariah_details_obj.cicilan_bulanan,
                                               'jml_cicilan': total_cicilan,
                                               'jml_pokok': pokok,
                                               'jml_bunga': bunga,
                                               'saldo_pinjaman_bln': P_bln,
                                               'state': 'paid'
                                               })
                    saldo_pinjaman = syariah_details_obj.saldo_pinjaman - total_cicilan
                    sql_query = """update yudha_peminjaman_syariah_details set saldo_pinjaman=%s where
                        loan_id=%s and id>=%s;
                        """
                    self.env.cr.execute(sql_query,(saldo_pinjaman, syariah.loan_id.id, syariah.detail_id.id,))
                    # Update Header
                    syariah_obj=self.env['yudha.peminjaman.syariah'].search([('id','=',syariah.loan_id.id)])
                    if syariah_obj:
                        syariah_obj.write({'jml_bayar':syariah_obj.jml_pinjam-P_bln,'sisa_loan':P_bln,'sisa_cicilan':syariah_obj.sisa_cicilan-1})
                    # sql_query = """update yudha_peminjaman_syariah set jml_bayar=jml_pinjam-%s, sisa_loan=%s where
                    #             id=%s ;
                    #             """
                    # self.env.cr.execute(sql_query, (P_bln, P_bln, syariah.loan_id.id,))

            #prepare journal
            acc_line = {'account_id': settings_obj.coa_tagihan_bulanan.id,
                        'name': 'Angsuran Pinjaman Syariah/KPR',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': angsuran_syariah,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            if pokok>0:
                acc_line = {'account_id': settings_obj.coa_piutang_anggota.id,
                            'name': 'Angsuran Pokok Pinjaman Syariah/KPR',
                            'analytic_account_id': acc_analytic.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': pokok}
                acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_jasa_pinjaman.id,
                        'name': 'Jasa Pinjaman Syariah/KPR',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': bunga}
            acc_detail.append((0, 0, acc_line))
        acc_header['line_ids'] = acc_detail
        create_journal = self.env['account.move'].create(acc_header)
        create_journal.post()
        self.move_id=create_journal.id

        #Update data peminjaman
        #Pinjaman Konsumtif
        if angsuran_konsumtif > 0:
            for konsumtif in self.konsumtif_ids:
                konsumtif_obj=self.env['yudha.peminjaman.konsumtif.details'].search([('id','=',konsumtif.detail_id.id)])
                if konsumtif_obj:
                    #Update Detail
                    sql_query="""select real_thr+real_ik+real_jasop as jumlah from yudha_validasi_potongan_thrikjasop where
                        jenis_pinjaman='konsumtif' and docnum=%s and thrikjasop_id=%s;
                        """
                    self.env.cr.execute(sql_query,(konsumtif_obj.loan_id.docnum,self.id,))
                    result = self.env.cr.dictfetchall()
                    jml_pokok = 0
                    for res in result:
                        jml_pokok=res['jumlah']
                    konsumtif_obj.write({'jml_pokok':jml_pokok,
                                         'rencana_cicilan':jml_pokok+konsumtif_obj.jml_bunga,
                                         'jml_cicilan':jml_pokok+konsumtif.realisasi,
                                         'state':'paid'
                                         })
                    saldo_pinjaman=konsumtif_obj.saldo_pinjaman - jml_pokok
                    sql_query = """update yudha_peminjaman_konsumtif_details set saldo_pinjaman=%s where
                        loan_id=%s and id>=%s;
                        """
                    self.env.cr.execute(sql_query,(saldo_pinjaman,konsumtif.loan_id.id,konsumtif.detail_id.id,))
                    # Update Header
                    konsumtif_header_obj = self.env['yudha.peminjaman.konsumtif'].search([('id', '=', konsumtif.loan_id.id)])
                    konsumtif_header_obj.write({'jml_bayar': konsumtif_header_obj.jml_pinjam - saldo_pinjaman, 'sisa_loan': saldo_pinjaman,
                                           'sisa_cicilan': konsumtif_header_obj.sisa_cicilan - 1})

                    # sql_query = """update yudha_peminjaman_konsumtif set jml_bayar=jml_pinjam-%s, sisa_loan=%s where
                    #             id=%s ;
                    #             """
                    # self.env.cr.execute(sql_query, (saldo_pinjaman,saldo_pinjaman, konsumtif.loan_id.id,))

        #2. Transfer Simpanan Pokok, Simpanan Wajib dan Simpanan Sukarela dari USP
        # ke HO (di database USP). Angka diambil dari saldo simpanan pokok/wajib/sukarela
        lstjr = self.get_last_journal()
        counter = str(lstjr + 1)
        nama_account = '%s/%s/%s' % ('KOPKARTRNS', tahun, counter)
        acc_header={}
        acc_detail=[]
        acc_header = {'date': fields.datetime.now(),
                      'journal_id': journal_id.id,
                      'company_id': mycomp,
                      'ref': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                      'name': nama_account}
        if simpanan_pokok>0:
            acc_line = {'account_id': settings_obj.coa_simp_pokok.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_pokok,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_kliring_usp.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_pokok}
            acc_detail.append((0, 0, acc_line))
        if simpanan_wajib>0:
            acc_line = {'account_id': settings_obj.coa_simp_wajib.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_wajib,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_kliring_usp.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_wajib}
            acc_detail.append((0, 0, acc_line))
        if simpanan_sukarela>0:
            acc_line = {'account_id': settings_obj.coa_simp_sukarela.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': simpanan_sukarela,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_kliring_usp.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': simpanan_sukarela}
            acc_detail.append((0, 0, acc_line))
        acc_header['line_ids'] = acc_detail
        create_journal = self.env['account.move'].create(acc_header)
        create_journal.post()
        self.move_id2 = create_journal.id

        #3. Catat Transfer Simpanan Pokok, Simpanan Wajib dan Simpanan Sukarela dari USP ke HO (di database HO)
        lstjr = self.get_last_journal()
        counter = str(lstjr + 1)
        ho_comp=self.env['res.company'].search([('name','=','Koperasi Karyawan Pupuk Kaltim (Kantor Pusat)')]).id
        nama_account = '%s/%s/%s' % ('KOPKARTRNS', tahun, counter)
        acc_analytic_ho = self.env['account.analytic.account'].search(['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', ho_comp)], limit=1)
        acc_header={}
        acc_detail=[]
        acc_header = {'date': fields.datetime.now(),
                      'journal_id': 60,
                      'company_id': ho_comp,
                      'ref': 'Transfer Simpanan Pokok, Wajib dan Sukarela dari USP',
                      'name': nama_account}
        if simpanan_pokok>0:
            acc_line = {'account_id': settings_obj.coa_kliring_ho.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela dari USP',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': simpanan_pokok,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_pokok.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': 0,
                        'credit': simpanan_pokok}
            acc_detail.append((0, 0, acc_line))
        if simpanan_wajib>0:
            acc_line = {'account_id': settings_obj.coa_kliring_ho.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': simpanan_wajib,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_wajib_ho.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': 0,
                        'credit': simpanan_wajib}
            acc_detail.append((0, 0, acc_line))
        if simpanan_sukarela>0:
            acc_line = {'account_id': settings_obj.coa_kliring_ho.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': simpanan_sukarela,
                        'credit': 0}
            acc_detail.append((0, 0, acc_line))
            acc_line = {'account_id': settings_obj.coa_simp_sukarela_ho.id,
                        'name': 'Transfer Simpanan Pokok, Wajib dan Sukarela ke HO',
                        'analytic_account_id': acc_analytic_ho.id,
                        'analytic_tag_ids': '',
                        'company_id': ho_comp,
                        'debit': 0,
                        'credit': simpanan_sukarela}
            acc_detail.append((0, 0, acc_line))
        acc_header['line_ids'] = acc_detail
        create_journal = self.env['account.move'].create(acc_header)
        create_journal.post()
        self.move_id3 = create_journal.id
        self.state = 'done'


    
    def validate_yuda(self):
        if self.state == 'done':
            raise UserError((
                                'Error!\n'
                                'Tidak dapat memvalidasi data untuk No Document %s karena sudah di Validasi ') % (
                                self.no_val))
        accmov = self.env['account.move']
        acc_header ={}
        acc_item2 = []

        mycomp = self._get_company_id()
        namaacc  = ''
        tahun = datetime.now().year
        lstjr=self.get_last_journal()
        #lstjr += 1
        #counter= 0000 + lstjr
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARTRNS',tahun,  counter)
        jid = self.env['account.journal'].search(
            [('name', '=', 'Unit Simpan Pinjam'), ('company_id', '=', mycomp)], limit=1)

        acc_anna = self.env['account.analytic.account'].search(
            ['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', mycomp)],
            limit=1)
        totsetoruang = 0
        tottarikuang = 0
        tottarikwajib = 0
        totsetorwajib = 0
        totsetordana = 0
        tottarikdana = 0
        totsetorbarang = 0
        tottarikbarang = 0
        totsetorkonsumtif = 0
        tottarikkonsumtif = 0
        totsetorsembako = 0
        tottariksembako = 0
        totsetorsyariah = 0
        tottariksyariah = 0
        totsetorpotongan = 0
        tottarikpotongan = 0
        for allwjb in self.wajib_ids:
            if allwjb.jns_trans =='SD':
                totsetorwajib += allwjb.amount
            else:
                tottarikwajib += allwjb.amount
        for allpnjdana in self.dana_ids:
            if allpnjdana.jns_trans =='SD':
                totsetordana += allpnjdana.amount
            else:
                tottarikdana += allpnjdana.amount
        for allpnjbrg in self.barang_ids:
            if allpnjbrg.jns_trans == 'SD':
                totsetorbarang += allpnjbrg.amount
            else:
                tottarikbarang += allpnjbrg.amount
        for allpnjkons in self.konsumtif_ids:
            if allpnjkons.jns_trans == 'SD':
                totsetorkonsumtif += allpnjkons.amount
            else:
                tottarikkonsumtif += allpnjkons.amount
        for allpnjsbk in self.sembako_ids:
            if allpnjsbk.jns_trans =='SD':
                totsetorsembako += allpnjsbk.amount
            else:
                tottariksembako += allpnjsbk.amount
        for allpnjsyr in self.syariah_ids:
            if allpnjsyr.jns_trans == 'SD':
                totsetorsyariah += allpnjsyr.amount
            else:
                tottariksyariah += allpnjsyr.amount
        for allpnjptot in self.tabungan_ids:
            if allpnjptot.jns_trans == 'SD':
                totsetorpotongan += allpnjptot.amount
            else:
                tottarikpotongan += allpnjptot.amount

        totsetoruang = totsetorwajib + totsetordana + totsetorbarang + totsetorkonsumtif + totsetorsembako + totsetorsyariah +totsetorpotongan
        tottarikuang = tottarikwajib + tottarikdana + tottarikbarang + tottarikkonsumtif + tottariksembako + tottariksyariah + tottarikpotongan
        if totsetoruang > 0:
            acc_header = {'date': fields.datetime.now(),
                          'journal_id': jid.id,
                          'company_id': mycomp,
                          'ref': 'Penerimaan Pembayaran Pinjaman',
                          'name': namaaccount}
            for x in range(0, 2):
                if x == 0:
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', '=', 'PIUTANG PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': '',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': 0,
                                'credit': totsetoruang}
                else:
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', '=', 'KLIRING PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': '',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': totsetoruang,
                                'credit': 0}
                acc_item2.append((0, 0, acc_line))
                acc_header['line_ids'] = acc_item2
            buat_jurnal_setor=self.env['account.move'].create(acc_header)
            buat_jurnal_setor.post()
            myval = self.env['yudha.validasi.bulanan'].search([('no_val','=',self.no_val)])
            if myval:
                mywajib = self.env['yudha.validasi.simpanan.wajib'].search([('wajib_id','=',myval.id)])
                if mywajib:
                    for allwajibs in mywajib:
                        allwajibs.write({'no_accmove':buat_jurnal_setor.id})
                mydanas = self.env['yudha.validasi.pinjaman.dana'].search([('dana_id','=',myval.id)])
                if mydanas:
                    for alldanas in  mydanas:
                        alldanas.write({'no_accmove': buat_jurnal_setor.id})
                mydanas = self.env['yudha.validasi.pinjaman.dana'].search([('dana_id','=',myval.id)])
                if mydanas:
                    for alldanas in mydanas:
                        alldanas.write({'no_accmove': buat_jurnal_setor.id})
                mybrgs = self.env['yudha.validasi.pinjaman.barang'].search([('barang_id','=',myval.id)])
                if mybrgs:
                    for allbrgs in mybrgs:
                        allbrgs.write({'no_accmove': buat_jurnal_setor.id})
                mykonss = self.env['yudha.validasi.pinjaman.konsumtif'].search([('konsumtif_id','=',myval.id)])
                if mykonss:
                    for allkonss in mykonss:
                        allkonss.write({'no_accmove': buat_jurnal_setor.id})
                mysbks = self.env['yudha.validasi.pinjaman.sembako'].search([('sembako_id','=',myval.id)])
                if mysbks:
                    for allsbks in mysbks:
                        allsbks.write({'no_accmove': buat_jurnal_setor.id})
                mysyrs = self.env['yudha.validasi.pinjaman.syariah'].search([('syariah_id','=',myval.id)])
                if mydanas:
                    for allsyrs in mysyrs:
                        allsyrs.write({'no_accmove': buat_jurnal_setor.id})
                mypotgaji = self.env['yudha.validasi.potongan.tabungan'].search([('tabungan_id','=',myval.id)])
                if mypotgaji:
                    for allpotgaji in mypotgaji:
                        allpotgaji.write({'no_accmove': buat_jurnal_setor.id})
            # myval = self.env['yudha.validasi.bulanan'].search([('no_val','=',self.no_val)])
            # if myval:
            #     mydetail = self.env['yudha.validasi.bulanan.details'].search([('valid_id','=',myval.id)])
            #     if mydetail:
            #         for alldet in mydetail:
            #             alldet.write({'no_accmove': buat_jurnal.id})
            #             alldet.write({'state': 'done'})
        elif tottarikuang > 0 :
            acc_header = {'date': fields.datetime.now(),
                          'journal_id': jid.id,
                          'company_id': mycomp,
                          'ref': 'Peminjaman kepada Anggota',
                          'name': namaaccount}
            for x in range(0, 2):
                if x == 0:
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', '=', 'PIUTANG PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': '',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': tottarikuang,
                                'credit': 0}
                else:
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', '=', 'KLIRING PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': '',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': 0,
                                'credit': tottarikuang}
                acc_item2.append((0, 0, acc_line))
                acc_header['line_ids'] = acc_item2
            buat_jurnal_tarik=self.env['account.move'].create(acc_header)
            buat_jurnal_tarik.post()
            myval = self.env['yudha.validasi.bulanan'].search([('no_val','=',self.no_val)])
            if myval:
                mywajib = self.env['yudha.validasi.simpanan.wajib'].search([('wajib_id','=',myval.id)])
                if mywajib:
                    for allwajibs in mywajib:
                        allwajibs.write({'no_accmove':buat_jurnal_tarik.id})
                mydanas = self.env['yudha.validasi.pinjaman.dana'].search([('dana_id','=',myval.id)])
                if mydanas:
                    for alldanas in  mydanas:
                        alldanas.write({'no_accmove': buat_jurnal_tarik.id})
                mydanas = self.env['yudha.validasi.pinjaman.dana'].search([('dana_id','=',myval.id)])
                if mydanas:
                    for alldanas in mydanas:
                        alldanas.write({'no_accmove': buat_jurnal_tarik.id})
                mybrgs = self.env['yudha.validasi.pinjaman.barang'].search([('barang_id','=',myval.id)])
                if mybrgs:
                    for allbrgs in mybrgs:
                        allbrgs.write({'no_accmove': buat_jurnal_tarik.id})
                mykonss = self.env['yudha.validasi.pinjaman.konsumtif'].search([('konsumtif_id','=',myval.id)])
                if mykonss:
                    for allkonss in mykonss:
                        allkonss.write({'no_accmove': buat_jurnal_tarik.id})
                mysbks = self.env['yudha.validasi.pinjaman.sembako'].search([('sembako_id','=',myval.id)])
                if mysbks:
                    for allsbks in mysbks:
                        allsbks.write({'no_accmove': buat_jurnal_tarik.id})
                mysyrs = self.env['yudha.validasi.pinjaman.syariah'].search([('syariah_id','=',myval.id)])
                if mydanas:
                    for allsyrs in mysyrs:
                        allsyrs.write({'no_accmove': buat_jurnal_tarik.id})
                mypotgaji = self.env['yudha.validasi.potongan.tabungan'].search([('tabungan_id','=',myval.id)])
                if mypotgaji:
                    for allpotgaji in mypotgaji:
                        allpotgaji.write({'no_accmove': buat_jurnal_tarik.id})
        for allwjb in self.wajib_ids:
            if allwjb.jns_trans =='SD':
                self._update_kontak_bayar(allwjb.no_trans,buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allwjb.no_trans,buat_jurnal_tarik.id)
        for allpnjdana in self.dana_ids:
            if allpnjdana.jns_trans =='SD':
                self._update_kontak_bayar(allpnjdana.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjdana.no_trans, buat_jurnal_tarik.id)

        for allpnjbrg in self.barang_ids:
            if allpnjbrg.jns_trans == 'SD':
                self._update_kontak_bayar(allpnjbrg.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjbrg.no_trans, buat_jurnal_tarik.id)
        for allpnjkons in self.konsumtif_ids:
            if allpnjkons.jns_trans == 'SD':
                self._update_kontak_bayar(allpnjkons.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjkons.no_trans, buat_jurnal_tarik.id)
        for allpnjsbk in self.sembako_ids:
            if allpnjsbk.jns_trans =='SD':
                self._update_kontak_bayar(allpnjsbk.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjsbk.no_trans, buat_jurnal_tarik.id)
        for allpnjsyr in self.syariah_ids:
            if allpnjsyr.jns_trans == 'SD':
                self._update_kontak_bayar(allpnjsyr.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjsyr.no_trans, buat_jurnal_tarik.id)
        for allpnjptot in self.tabungan_ids:
            if allpnjptot.jns_trans == 'SD':
                self._update_kontak_bayar(allpnjptot.no_trans, buat_jurnal_setor.id)
            else:
                self._update_kontak_pinjam(allpnjptot.no_trans, buat_jurnal_tarik.id)
        self.write({'state': 'done'})


class yudha_validasi_simpanan_wajib(models.Model):
    _name = 'yudha.validasi.simpanan.wajib'

    wajib_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Simpanan Wajib Details", required=False,store=True,index=True )
    jns_simpanan = fields.Selection([('pokok', 'Pokok'), ('wajib', 'Wajib'),('rela', 'Sukarela')], string='Jenis Simpanan', help='Jenis Simpanan')
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    amount = fields.Float('Amount', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')
    no_trans = fields.Char(size=100, string='No. Transaksi')


class yudha_validasi_pinjaman_dana(models.Model):
    _name = 'yudha.validasi.pinjaman.dana'

    dana_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Pinjaman Dana Details", required=False,store=True,index=True )
    detail_id = fields.Many2one('yudha.peminjaman.dana.details', string="ID Pinjaman Dana Details", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    jml_pokok = fields.Float('Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga = fields.Float('Bunga', digits=(16, 2), store=True, default=0)
    amount = fields.Float('Total', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')

class yudha_validasi_pinjaman_barang(models.Model):
    _name = 'yudha.validasi.pinjaman.barang'

    barang_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Pinjaman Barang Details", required=False,store=True,index=True )
    detail_id = fields.Many2one('yudha.peminjaman.barang.details', string="ID Pinjaman Barang Details", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    jml_pokok = fields.Float('Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga = fields.Float('Bunga', digits=(16, 2), store=True, default=0)
    amount = fields.Float('Total', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')

class yudha_validasi_konsumtif(models.Model):
    _name = 'yudha.validasi.pinjaman.konsumtif'

    konsumtif_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Pinjaman Konsumtif Details", required=False,store=True,index=True )
    detail_id = fields.Many2one('yudha.peminjaman.konsumtif.details', string="ID Pinjaman Konsumtif Details", required=False,store=True,index=True )
    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.konsumtif", inverse_name='id', string="No Pinjaman",
                              required=False, default=False)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    amount = fields.Float('Bunga', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')


class yudha_validasi_pinjaman_sembako(models.Model):
    _name = 'yudha.validasi.pinjaman.sembako'

    sembako_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Pinjaman Sembako Details", required=False,store=True,index=True )
    detail_id = fields.Many2one('yudha.peminjaman.sembako.details', string="ID Pinjaman Sembako Details", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    amount = fields.Float('Amount', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')

class yudha_validasi_pinjaman_syariah(models.Model):
    _name = 'yudha.validasi.pinjaman.syariah'

    syariah_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Pinjaman Syariah Details", required=False,store=True,index=True )
    detail_id = fields.Many2one('yudha.peminjaman.syariah.details', string="ID Pinjaman Syariah Details", required=False,store=True,index=True )
    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.syariah", inverse_name='id', string="No Pinjaman",
                              required=False, default=False)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    jml_pokok = fields.Float('Pokok', digits=(16, 2), store=True, default=0)
    jml_bunga = fields.Float('Bunga', digits=(16, 2), store=True, default=0)
    amount = fields.Float('Total', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')

class yudha_validasi_potongan_tabungan(models.Model):
    _name = 'yudha.validasi.potongan.tabungan'

    tabungan_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Potongan Tabungan Details", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    amount = fields.Float('Amount', digits=(19, 2), default=0, required=True)
    realisasi = fields.Float('Realisasi', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')

class yudha_validasi_potongan_thrikjasop(models.Model):
    _name = 'yudha.validasi.potongan.thrikjasop'

    thrikjasop_id = fields.Many2one('yudha.validasi.bulanan', string="Validasi Potongan THR/IK/JAPOS Details", required=False,store=True,index=True )
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=False, domain="[('category_id', '=', 'Anggota')]")
    docnum = fields.Char(size=100, string='No Pinjaman')
    no_anggota = fields.Char(size=100, string='No Anggota')
    npk = fields.Char(size=100, string='NPK')
    unit_kerja = fields.Char(size=100, string='Unit Kerja')
    asal_pt = fields.Many2one(comodel_name="yudha.asal.perusahaan", inverse_name='id', string="Asal Perusahaan")
    jenis_pinjaman = fields.Selection([('konsumtif', 'Konsumtif'), ('syariah', 'Syariah/KPR')], string='Jenis Pinjaman',help='Jenis Pinjaman')
    type_potongan = fields.Selection([('persen', 'Persentase'), ('amount', 'Amount')], string='Type Potongan')
    pot_thr = fields.Float('Pot. THR', digits=(19, 2), default=0, required=True)
    pot_ik = fields.Float('Pot. IK', digits=(19, 2), default=0, required=True)
    pot_jasop = fields.Float('Pot. JASOP', digits=(19, 2), default=0, required=True)
    real_thr = fields.Float('Realisasi THR', digits=(19, 2), default=0, required=True)
    real_ik = fields.Float('Realisasi IK', digits=(19, 2), default=0, required=True)
    real_jasop = fields.Float('Realisasi JASOP', digits=(19, 2), default=0, required=True)
    state = fields.Char(size=100, string='State', default='ready')