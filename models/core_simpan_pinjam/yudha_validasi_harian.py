# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import uuid
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import datetime

SESSION_STATES = [
        ('ready', 'Ready'),
        ('done', 'Done')
]

class yudha_validasi_harian(models.Model):
    _name = 'yudha.validasi.harian'
    _order = 'no_val desc'
    _description = "yudha VALIDASI HARIAN"

    confirm_by = fields.Many2one('res.users',string='Confirm By',readonly='1', default=lambda self: self.env.user)
    #no_val = fields.Char(string='No. Validasi', default=lambda self: self.env['ir.sequence'].next_by_code('yudha.validasi.harian.1'),index=True,copy=True,required=True)
    no_val = fields.Char(string='No. Validasi', index=True,copy=True)
    jns_dok = fields.Char(string='Jenis Dokument', default='Validasi Harian',index=True,copy=True,required=True, readonly=True)
    tgl_val = fields.Date(string='Tanggal Validasi', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    #tipe_trans = fields.Selection([('SP', 'Simpanan Pokok'), ('SW', 'Simpanan Wajib'),('SS','Simpanan Sukarela'),('TAB','Tabungan'),('DP','Simpanan Berjangka'),('pin_dana','Pinjaman Dana'),('pin_barang','Pinjaman Barang'),('pin_kons','Pinjaman Konsumtif'),('pin_syr','Pinjaman Syariah'),('pin_sembako','Pinjaman Sembako')], string='Tipe Transaksi', help='Tipe Transaksi')
    #tipe_trans= fields.Selection([('SP', 'Simpanan Pokok'), ('SW', 'Simpanan Wajib')], string='Tipe Transaksi', help='Tipe Transaksi')
    #no_trans  = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='No. Transaksi', help='No. Transaksi')
    valsimpok_ids = fields.One2many(comodel_name='yudha.validasi.simpanan.pokok',inverse_name="valsimpok_id",string='Validasi Simpanan Pokok')
    valsimsuka_ids = fields.One2many(comodel_name='yudha.validasi.simpanan.sukarela',inverse_name="valsimsuka_id",string='Validasi Simpanan Sukarela')
    valtab_ids = fields.One2many(comodel_name='yudha.validasi.tabungan',inverse_name="valtab_id",string='Validasi Tabungan')
    valdepo_ids = fields.One2many(comodel_name='yudha.validasi.deposito',inverse_name="valdepo_id",string='Validasi Deposito')
    valpinjam_ids = fields.One2many(comodel_name='yudha.validasi.pinjaman',inverse_name="valid_id",string='Validasi Pelunasan Pinjaman')
    vallunas_ids = fields.One2many(comodel_name='yudha.validasi.pelunasan.pinjaman',inverse_name="valid_id",string='Validasi Pelunasan Pinjaman')

    keterangan = fields.Char(size=100, string='Keterangan')
    state = fields.Selection(string="State", selection=SESSION_STATES,
                             required=False,
                             readonly=True,
                             track_visibility='onchange',
                             default=SESSION_STATES[0][0])

    
    def name_get(self):
        result = []
        for s in self:
            date_invoice = datetime.strptime(s.tgl_val, "%Y-%m-%d").strftime("%d-%m-%Y")
            name = 'Validasi: ' + str(s.no_val) + ' - Date : ' + date_invoice
            result.append((s.id, name))
        return result
        #return super(yudha_validasi_harian, self).name_get()

    @api.model
    def create(self, vals):
        DATETIME_FORMAT = "%Y-%m-%d"
        if vals.get('tgl_val', False):
            dtim = vals['tgl_val']
        else:
            dtim = self.tgl_val
        timbang_date = datetime.strptime(dtim, DATETIME_FORMAT)
        tahun = timbang_date.strftime('%y')
        tahun2 = timbang_date.strftime('%Y')

        myquery = """SELECT max(no_val) FROM yudha_validasi_harian;"""
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
            vals['no_val'] = 'SIMVALHAR/' + str(tahun2) + '/' + str(nomerurut)
        else:
            vals['no_val'] ='SIMVALHAR/'+ str(tahun2) + '/' + '1'
        vals['state'] = 'ready'
        return super(yudha_validasi_harian, self).create(vals)

    def unlink(self):
        if self.state == 'done':
            raise UserError((
                                'Validasi Harian, Error!\n'
                                'No Document %s tidak dapat dihapus, karena sudah di Validasi ') % (
                                self.no_val))
        else:
            return super(yudha_validasi_harian, self).unlink()
    def _get_company_id(self):
        idnya = self.env.uid
        # print('line 89', idnya)
        mmsql="""SELECT b.id FROM res_users a INNER JOIN res_company b ON a.company_id=b.id where a.id=%s;"""
        self.env.cr.execute(mmsql, (idnya,))
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return

    def masuk_details_simpok(self, notrans, noacc,  tunai, trns, jnt,rek_agt,nm_b,atas,nrek):
        res = []
        res2 = []
        for field_rekap in self.valsimpok_ids:
            rekap_lines = {
                'valdepo_id': field_rekap['valsimpok_id'],
                'no_trans': field_rekap['no_trans'],
                'no_accmove': field_rekap['no_accmove'],
                'tunai': field_rekap['tunai'],
                'transfer': field_rekap['transfer'],
                'jns_trans': field_rekap['jns_trans'],
                'no_rek_agt': field_rekap['no_rek_agt'],
                'nm_bank': field_rekap['nm_bank'],
                'atas_nama': field_rekap['atas_nama'],
                'no_rek': field_rekap['no_rek'],
            }
            res2 += [rekap_lines]
        add_line = {'valsimpok_id': self._origin.id,
                    'no_trans': notrans,
                    'no_accmove': noacc,
                    'tunai': tunai,
                    'transfer': trns,
                    'jns_trans': jnt,
                    'no_rek_agt': rek_agt,
                    'nm_bank': nm_b,
                    'atas_nama': atas,
                    'no_rek': nrek,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_details_simsuka(self, notrans, noacc,  tunai, trns, jnt,rek_agt,nm_b,atas,nrek):
        res = []
        res2 = []
        for field_rekap in self.valsimsuka_ids:
            rekap_lines = {
                'valdepo_id': field_rekap['valsimsuka_id'],
                'no_trans': field_rekap['no_trans'],
                'no_accmove': field_rekap['no_accmove'],
                'tunai': field_rekap['tunai'],
                'transfer': field_rekap['transfer'],
                'jns_trans': field_rekap['jns_trans'],
                'no_rek_agt': field_rekap['no_rek_agt'],
                'nm_bank': field_rekap['nm_bank'],
                'atas_nama': field_rekap['atas_nama'],
                'no_rek': field_rekap['no_rek'],
            }
            res2 += [rekap_lines]
        add_line = {'valsimsuka_id': self._origin.id,
                    'no_trans': notrans,
                    'no_accmove': noacc,
                    'tunai': tunai,
                    'transfer': trns,
                    'jns_trans': jnt,
                    'no_rek_agt': rek_agt,
                    'nm_bank': nm_b,
                    'atas_nama': atas,
                    'no_rek': nrek,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_details_tab(self, notrans,jtab, noacc,  tunai, trns, jnt,rek_agt,nm_b,atas,nrek):
        res = []
        res2 = []
        for field_rekap in self.valtab_ids:
            rekap_lines = {
                'valdepo_id': field_rekap['valtab_id'],
                'no_trans': field_rekap['no_trans'],
                'jns_tab': field_rekap['jns_tab'],
                'no_accmove': field_rekap['no_accmove'],
                'tunai': field_rekap['tunai'],
                'transfer': field_rekap['transfer'],
                'jns_trans': field_rekap['jns_trans'],
                'no_rek_agt': field_rekap['no_rek_agt'],
                'nm_bank': field_rekap['nm_bank'],
                'atas_nama': field_rekap['atas_nama'],
                'no_rek': field_rekap['no_rek'],
            }
            res2 += [rekap_lines]
        add_line = {'valtab_id': self._origin.id,
                    'no_trans': notrans,
                    'jns_tab': jtab,
                    'no_accmove': noacc,
                    'tunai': tunai,
                    'transfer': trns,
                    'jns_trans': jnt,
                    'no_rek_agt': rek_agt,
                    'nm_bank': nm_b,
                    'atas_nama': atas,
                    'no_rek': nrek,
                    }
        res += [add_line]
        res += res2
        return res

    def masuk_details_depo(self, notrans, jnsdepo, noacc,  tunai, trns, jnt,rek_agt,nm_b,atas,nrek):
        res = []
        res2 = []
        norut = 0
        new_line = 'Y'
        for field_rekap in self.valdepo_ids:
            rekap_lines = {
                'valdepo_id': field_rekap['valdepo_id'],
                'no_trans': field_rekap['no_trans'],
                'no_accmove': field_rekap['no_accmove'],
                'tunai': field_rekap['tunai'],
                'transfer': field_rekap['transfer'],
                'jns_trans': field_rekap['jns_trans'],
                'no_rek_agt': field_rekap['no_rek_agt'],
                'nm_bank': field_rekap['nm_bank'],
                'atas_nama': field_rekap['atas_nama'],
                'no_rek': field_rekap['no_rek'],
                'jns_depo': field_rekap['jns_depo'],
            }
            res2 += [rekap_lines]
        add_line = {'valdepo_id': self._origin.id,
                    'no_trans': notrans,
                    'no_accmove': noacc,
                    'tunai': tunai,
                    'transfer': trns,
                    'jns_trans': jnt,
                    'no_rek_agt': rek_agt,
                    'nm_bank': nm_b,
                    'atas_nama': atas,
                    'no_rek': nrek,
                    'jns_depo': jnsdepo,
                    }
        res += [add_line]
        res += res2
        return res

    @api.onchange('tgl_val')
    def onchange_tgl_val(self):
        if not self.tgl_val:
            return
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date = datetime.strptime(self.tgl_val, DATETIME_FORMAT)
        tanggalan = timbang_date.strftime('%Y-%m-%d')
        self.valsimpok_ids =[]
        self.valsimsuka_ids = []
        self.valtab_ids = []
        self.valdepo_ids = []
        # compid = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        # mycomp = self.env['res.company'].search([('id','=',compid.company_id)])
        datasimpok = self.env['yudha.iuran.pokok'].search([('tgl_trans','=',tanggalan)])
        #datasimpok = self.get_simpok(tanggalan,self.jns_trans)
        if not datasimpok is None:
            for allsimpok in datasimpok:
                if allsimpok.asal_dana =='CS':
                    self.valsimpok_ids = self.masuk_details_simpok(allsimpok.docnum,allsimpok.no_accmove,allsimpok.amount,0,allsimpok.jns_trans,'','','','')
                else:
                    self.valsimpok_ids = self.masuk_details_simpok(allsimpok.docnum,allsimpok.no_accmove,0,allsimpok.amount,allsimpok.jns_trans,allsimpok.no_rek_agt,allsimpok.nm_bank,allsimpok.atasnama,allsimpok.no_rek_bank)
        else:
            self.valsimpok_ids = []
        datasimsuka = self.env['yudha.iuran.sukarela'].search([('tgl_trans','=',tanggalan)])
        if not datasimsuka is None:
            for allsimsuka in datasimsuka:
                if allsimsuka.asal_dana == 'CS':
                    self.valsimsuka_ids = self.masuk_details_simsuka(allsimsuka.docnum, allsimsuka.no_accmove, allsimsuka.amount,0,allsimsuka.jns_trans,'','','','')
                else:
                    self.valsimsuka_ids = self.masuk_details_simsuka(allsimsuka.docnum, allsimsuka.no_accmove, 0, allsimsuka.amount, allsimsuka.jns_trans,allsimsuka.no_rek_agt,allsimsuka.nm_bank,allsimsuka.atasnama,allsimsuka.no_rek_bank)
        else:
            self.valsimsuka_ids = []
        datatab = self.env['yudha.tabungan'].search([('tgl_trans','=',tanggalan)])
        if not datatab is None:
            for alltab in datatab:
                if alltab.asal_dana == 'CS':
                    self.valtab_ids = self.masuk_details_tab(alltab.docnum,alltab.jenis_tabungan, alltab.no_accmove, alltab.jml_tab, 0, alltab.jns_trans,'','','','')
                else:
                    self.valtab_ids = self.masuk_details_tab(alltab.docnum,alltab.jenis_tabungan, alltab.no_accmove, 0, alltab.jml_tab, alltab.jns_trans, alltab.no_rek_agt, alltab.nm_bank,alltab.atasnama,alltab.no_rek_bank)
        else:
            self.valtab_ids = []
        datadepo = self.env['yudha.deposito'].search([('tgl_trans', '=', tanggalan)])
        if not datadepo is None:
            for alldepo in datadepo:
                if alldepo.asal_dana == 'CS':
                    self.valdepo_ids = self.masuk_details_depo(alldepo.docnum,alldepo.jns_depo, alldepo.no_accmove, alldepo.jml_depo, 0, alldepo.jns_trans,'','','','')
                else:
                    self.valdepo_ids = self.masuk_details_depo(alldepo.docnum, alldepo.jns_depo, alldepo.no_accmove, 0, alldepo.jml_depo, alldepo.jns_trans, alldepo.no_rek_agt, alldepo.nm_bank,alldepo.atasnama,alldepo.no_rek_bank)
        else:
            self.valdepo_ids = []

        res = []
        peminjaman_rekap = self.env['yudha.peminjaman.dana'].search([('tgl_trans', '=', tanggalan)])
        if not peminjaman_rekap is None:
            for field_rekap in peminjaman_rekap:
                rekap_lines = {
                    'docnum': field_rekap['docnum'],
                    'tgl_trans': field_rekap['tgl_trans'],
                    'partner_id': field_rekap['partner_id'],
                    'no_agt': field_rekap['no_agt'],
                    'jml_pinjam': field_rekap['jml_pinjam'],
                    'keterangan': field_rekap['keterangan'],
                    'nm_trans': field_rekap['nm_trans'],
                }
                res += [rekap_lines]
        peminjaman_rekap = self.env['yudha.peminjaman.barang'].search([('tgl_trans', '=', tanggalan)])
        if not peminjaman_rekap is None:
            for field_rekap in peminjaman_rekap:
                rekap_lines = {
                    'docnum': field_rekap['docnum'],
                    'tgl_trans': field_rekap['tgl_trans'],
                    'partner_id': field_rekap['partner_id'],
                    'no_agt': field_rekap['no_agt'],
                    'jml_pinjam': field_rekap['jml_pinjam'],
                    'keterangan': field_rekap['keterangan'],
                    'nm_trans': field_rekap['nm_trans'],
                }
                res += [rekap_lines]
        peminjaman_rekap = self.env['yudha.peminjaman.konsumtif'].search([('tgl_trans', '=', tanggalan)])
        if not peminjaman_rekap is None:
            for field_rekap in peminjaman_rekap:
                rekap_lines = {
                    'docnum': field_rekap['docnum'],
                    'tgl_trans': field_rekap['tgl_trans'],
                    'partner_id': field_rekap['partner_id'],
                    'no_agt': field_rekap['no_agt'],
                    'jml_pinjam': field_rekap['jml_pinjam'],
                    'keterangan': field_rekap['keterangan'],
                    'nm_trans': field_rekap['nm_trans'],
                }
                res += [rekap_lines]
        peminjaman_rekap = self.env['yudha.peminjaman.sembako'].search([('tgl_trans', '=', tanggalan)])
        if not peminjaman_rekap is None:
            for field_rekap in peminjaman_rekap:
                rekap_lines = {
                    'docnum': field_rekap['docnum'],
                    'tgl_trans': field_rekap['tgl_trans'],
                    'partner_id': field_rekap['partner_id'],
                    'no_agt': field_rekap['no_agt'],
                    'jml_pinjam': field_rekap['jml_pinjam'],
                    'keterangan': field_rekap['keterangan'],
                    'nm_trans': field_rekap['nm_trans'],
                }
                res += [rekap_lines]
        peminjaman_rekap = self.env['yudha.peminjaman.syariah'].search([('tgl_trans', '=', tanggalan)])
        if not peminjaman_rekap is None:
            for field_rekap in peminjaman_rekap:
                rekap_lines = {
                    'docnum': field_rekap['docnum'],
                    'tgl_trans': field_rekap['tgl_trans'],
                    'partner_id': field_rekap['partner_id'],
                    'no_agt': field_rekap['no_agt'],
                    'jml_pinjam': field_rekap['jml_pinjam'],
                    'keterangan': field_rekap['keterangan'],
                    'nm_trans': field_rekap['nm_trans'],
                }
                res += [rekap_lines]

        self.valpinjam_ids = res
        
        res = []
        pelunasan_rekap = self.env['yudha.pelunasan.dana'].search([('date_pay', '=', tanggalan)])
        if not pelunasan_rekap is None:
            for field_rekap in pelunasan_rekap:
                pjm_obj=self.env['yudha.peminjaman.dana'].search([('id','=',field_rekap['loan_id'].id),('state','in',('paid','done'))])
                rekap_lines = {
                    'date_pay': field_rekap['date_pay'],
                    'doc_type': field_rekap['doc_type'],
                    'asal_dana': field_rekap['asal_dana'],
                    'partner_id': pjm_obj.partner_id.id,
                    'no_agt': pjm_obj.no_agt,
                    'loan_id': field_rekap['loan_id'],
                    'date_loan': pjm_obj.tgl_trans,
                    'amount': field_rekap['amount'],
                    'payment_type': 'dana',
                }
                res += [rekap_lines]
        pelunasan_rekap = self.env['yudha.pelunasan.barang'].search([('date_pay', '=', tanggalan)])
        if not pelunasan_rekap is None:
            for field_rekap in pelunasan_rekap:
                pjm_obj=self.env['yudha.peminjaman.barang'].search([('id','=',field_rekap['loan_id'].id),('state','in',('paid','done'))])
                rekap_lines = {
                    'date_pay': field_rekap['date_pay'],
                    'doc_type': field_rekap['doc_type'],
                    'asal_dana': field_rekap['asal_dana'],
                    'partner_id': pjm_obj.partner_id.id,
                    'no_agt': pjm_obj.no_agt,
                    'loan_id': field_rekap['loan_id'],
                    'date_loan': pjm_obj.tgl_trans,
                    'amount': field_rekap['amount'],
                    'payment_type': 'barang',
                }
                res += [rekap_lines]
        pelunasan_rekap = self.env['yudha.pelunasan.konsumtif'].search([('date_pay', '=', tanggalan)])
        if not pelunasan_rekap is None:
            for field_rekap in pelunasan_rekap:
                pjm_obj=self.env['yudha.peminjaman.konsumtif'].search([('id','=',field_rekap['loan_id'].id),('state','in',('paid','done'))])
                rekap_lines = {
                    'date_pay': field_rekap['date_pay'],
                    'doc_type': field_rekap['doc_type'],
                    'asal_dana': field_rekap['asal_dana'],
                    'partner_id': pjm_obj.partner_id.id,
                    'no_agt': pjm_obj.no_agt,
                    'loan_id': field_rekap['loan_id'],
                    'date_loan': pjm_obj.tgl_trans,
                    'amount': field_rekap['amount'],
                    'payment_type': 'konsumtif',
                }
                res += [rekap_lines]
        pelunasan_rekap = self.env['yudha.pelunasan.sembako'].search([('date_pay', '=', tanggalan)])
        if not pelunasan_rekap is None:
            for field_rekap in pelunasan_rekap:
                pjm_obj=self.env['yudha.peminjaman.sembako'].search([('id','=',field_rekap['loan_id'].id),('state','in',('paid','done'))])
                rekap_lines = {
                    'date_pay': field_rekap['date_pay'],
                    'doc_type': field_rekap['doc_type'],
                    'asal_dana': field_rekap['asal_dana'],
                    'partner_id': pjm_obj.partner_id.id,
                    'no_agt': pjm_obj.no_agt,
                    'loan_id': field_rekap['loan_id'],
                    'date_loan': pjm_obj.tgl_trans,
                    'amount': field_rekap['amount'],
                    'payment_type': 'sembako',
                }
                res += [rekap_lines]
        pelunasan_rekap = self.env['yudha.pelunasan.syariah'].search([('date_pay', '=', tanggalan)])
        if not pelunasan_rekap is None:
            for field_rekap in pelunasan_rekap:
                pjm_obj=self.env['yudha.peminjaman.syariah'].search([('id','=',field_rekap['loan_id'].id),('state','in',('paid','done'))])
                rekap_lines = {
                    'date_pay': field_rekap['date_pay'],
                    'doc_type': field_rekap['doc_type'],
                    'asal_dana': field_rekap['asal_dana'],
                    'partner_id': pjm_obj.partner_id.id,
                    'no_agt': pjm_obj.no_agt,
                    'loan_id': field_rekap['loan_id'],
                    'date_loan': pjm_obj.tgl_trans,
                    'amount': field_rekap['amount'],
                    'payment_type': 'syariah',
                }
                res += [rekap_lines]

        self.vallunas_ids = res


    def get_last_journal(self):
        #mmsql = """SELECT count(name) FROM account_move;"""
        mmsql="""SELECT max(id) FROM account_move;"""
        self.env.cr.execute(mmsql,)
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return 0


    def _update_setor_status(self,dcn, nmove):
        if str(dcn).find('SIMPOK') != -1:
            mysql = """SELECT a.partner_id, a.amount FROM yudha_iuran_pokok a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpok = res_partner_obj.iuran_pokok + res['amount']
                        res_partner_obj.write({'iuran_pokok': totpok})
                    else:
                        res_partner_obj.write({'iuran_pokok': res['amount']})
                res_dtl = self.env['yudha.iuran.pokok'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMSKR') != -1:
            mysql = """SELECT a.partner_id, a.amount FROM yudha_iuran_sukarela a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsuka = res_partner_obj.iuran_sukarela + res['amount']
                        res_partner_obj.write({'iuran_sukarela': totsuka})
                    else:
                        res_partner_obj.write({'iuran_sukarela': res['amount']})
                res_dtl = self.env['yudha.iuran.sukarela'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMTAB') != -1:
            mysql = """SELECT a.partner_id, a.jml_tab,c.name FROM yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id INNER JOIN account_account c ON b.akun_coa=c.id where docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        if res['name'] =='TABUNGAN ANGGOTA':
                          tottab = res_partner_obj.saldo_tab_agt + res['jml_tab']
                          res_partner_obj.write({'saldo_tab_agt': res['jml_tab']})
                          res_partner_obj.write({'tab_agt_bln': tottab})
                        elif res['name'] =='TABUNGAN MASYARAKAT':
                          tottab = res_partner_obj.saldo_masyarakat_bln + res['jml_tab']
                          res_partner_obj.write({'saldo_masyarakat_bln': res['jml_tab']})
                          res_partner_obj.write({'tab_masyarakat_bln': tottab})
                        else:
                            tottab = res_partner_obj.saldo_tab_khusus + res['jml_tab']
                            res_partner_obj.write({'saldo_tab_khusus': res['jml_tab']})
                            res_partner_obj.write({'tab_khusus_bln': tottab})
                    else:
                        if res['name'] == 'TABUNGAN ANGGOTA':
                            res_partner_obj.write({'saldo_tab_agt': res['jml_tab']})
                            res_partner_obj.write({'tab_agt_bln': res['jml_tab']})
                        elif res['name'] == 'TABUNGAN MASYARAKAT':
                            res_partner_obj.write({'saldo_masyarakat_bln': res['jml_tab']})
                            res_partner_obj.write({'tab_masyarakat_bln':res['jml_tab']})
                        else:
                            res_partner_obj.write({'saldo_tab_khusus': res['jml_tab']})
                            res_partner_obj.write({'tab_khusus_bln': res['jml_tab']})
                res_dtl = self.env['yudha.tabungan'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    if res_dtl.asal_dana == 'CS':
                        res_dtl.write({'state': 'done'})
                    elif res_dtl.asal_dana == 'TF':
                        res_dtl.write({'state': 'done'})

        elif str(dcn).find('SIMDEPO') != -1:
            mysql = """SELECT a.partner_id, a.jml_depo,c.name FROM yudha_deposito a INNER JOIN yudha_master_jenis_deposito b ON a.jns_depo=b.id INNER JOIN account_account c ON b.akun_coa=c.id WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            totdepo = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totdepo = res_partner_obj.saldo_deposito + res['jml_depo']
                        res_partner_obj.write({'saldo_deposito': totdepo})
                    else:
                        res_partner_obj.write({'saldo_deposito': res['jml_depo']})
                res_dtl = self.env['yudha.deposito'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    if res_dtl.asal_dana=='CS':
                        res_dtl.write({'state': 'deposit' })
                    elif res_dtl.asal_dana=='TF':
                        res_dtl.write({'state': 'deposit' })

    def _update_tarik_status(self,dcn, nmove):
        if str(dcn).find('SIMPOK') != -1:
            mysql = """SELECT a.partner_id, a.amount FROM yudha_iuran_pokok a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totpok = res_partner_obj.iuran_pokok - res['amount']
                        res_partner_obj.write({'iuran_pokok': totpok})
                    else:
                        res_partner_obj.write({'iuran_pokok': res['amount']})
                res_dtl = self.env['yudha.iuran.pokok'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMSKR') != -1:
            mysql = """SELECT a.partner_id, a.amount FROM yudha_iuran_sukarela a WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            totsuka = 0
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsuka = res_partner_obj.iuran_sukarela - res['amount']
                        res_partner_obj.write({'iuran_sukarela': totsuka})
                    else:
                        res_partner_obj.write({'iuran_sukarela': res['amount']})
                res_dtl = self.env['yudha.iuran.sukarela'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    res_dtl.write({'state': 'done' })
        elif str(dcn).find('SIMTAB') != -1:
            mysql = """SELECT a.partner_id, a.jml_tab,c.name FROM yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id INNER JOIN account_account c ON b.akun_coa=c.id where docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        if res['name'] == 'TABUNGAN ANGGOTA':
                            tottab = res_partner_obj.saldo_tab_agt - res['jml_tab']
                            res_partner_obj.write({'saldo_tab_agt': res['jml_tab']})
                            res_partner_obj.write({'tab_agt_bln': tottab})
                        elif res['name'] == 'TABUNGAN MASYARAKAT':
                            tottab = res_partner_obj.saldo_masyarakat_bln - res['jml_tab']
                            res_partner_obj.write({'saldo_masyarakat_bln': res['jml_tab']})
                            res_partner_obj.write({'tab_masyarakat_bln': tottab})
                        else:
                            tottab = res_partner_obj.saldo_tab_khusus - res['jml_tab']
                            res_partner_obj.write({'saldo_tab_khusus': res['jml_tab']})
                            res_partner_obj.write({'tab_khusus_bln': tottab})
                    else:
                        if res['name'] == 'TABUNGAN ANGGOTA':
                            res_partner_obj.write({'saldo_tab_agt': res['jml_tab']})
                            res_partner_obj.write({'tab_agt_bln': res['jml_tab']})
                        elif res['name'] == 'TABUNGAN MASYARAKAT':
                            res_partner_obj.write({'saldo_masyarakat_bln': res['jml_tab']})
                            res_partner_obj.write({'tab_masyarakat_bln':res['jml_tab']})
                        else:
                            res_partner_obj.write({'saldo_tab_khusus': res['jml_tab']})
                            res_partner_obj.write({'tab_khusus_bln': res['jml_tab']})

                res_dtl = self.env['yudha.tabungan'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    if res_dtl.asal_dana == 'CS':
                        res_dtl.write({'state': 'done'})
                    elif res_dtl.asal_dana == 'TF':
                        res_dtl.write({'state': 'valid'})
        elif str(dcn).find('SIMDEPO') != -1:
            mysql = """SELECT b.partner_id, b.jml_depo FROM yudha_deposito a INNER JOIN yudha_deposito_details b ON a.id=b.deposito_val WHERE a.docnum=%s;"""
            self.env.cr.execute(mysql, (dcn, ))
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    res_partner_obj = self.env['res.partner'].search([('id', '=', res['partner_id'])])
                    if res_partner_obj:
                        totsuka = res_partner_obj.saldo_depositob - res['jml_depo']
                        res_partner_obj.write({'saldo_deposito': totsuka})
                    else:
                        res_partner_obj.write({'saldo_deposito': res['jml_depo']})
                res_dtl = self.env['yudha.deposito'].search([('docnum','=',dcn)])
                if res_dtl:
                    res_dtl.write({'no_accmove': nmove})
                    if res_dtl.asal_dana == 'CS':
                        res_dtl.write({'state': 'paid'})
                    elif res_dtl.asal_dana == 'TF':
                        res_dtl.write({'state': 'valid'})

    def is_tab_transfer(self,dcn, tgl):
        mytab = self.env['yudha.tabungan'].search([('no_trans', '=', dcn), ('tgl_trans', '=', tgl)])
        if not mytab is None:
            for alltab in mytab:
                if alltab.asal_dana == 'TF':
                    return True
                else:
                    return False

    def get_simpok_setor_transfer_sama(self,tglnya):
        mysql = """SELECT sum(a.amount) FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.no_rek_bank=%s AND a.jns_trans='SD';"""
        self.env.cr.execute(mysql, (tglnya,))
        res = self.env.cr.fetchone()[0]
        if not res is None:
            return res
        else:
            return 0

    def get_simpok_group_sd(self,tglnya):
        #mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        mysql = """SELECT jns_trans,asal_dana, sum(amount), nm_bank, no_rek_bank, COUNT( * )  AS total_muncul FROM yudha_iuran_pokok WHERE tgl_trans = %s and jns_trans='SD' group by no_rek_bank,amount,jns_trans,asal_dana,nm_bank;"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnst = res['jns_trans']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'jns_trans': jnst,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb,}
                semua_hasil += [hasil]
            return semua_hasil

    def get_simpok_group_td(self,tglnya):
        #mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        mysql = """SELECT jns_trans, asal_dana, sum(amount), nm_bank, no_rek_bank, COUNT( * )  AS total_muncul FROM yudha_iuran_pokok WHERE tgl_trans = %s and jns_trans='TD' group by no_rek_bank,amount,jns_trans,asal_dana,nm_bank"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnst = res['jns_trans']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'jns_trans': jnst,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb,}
                semua_hasil += [hasil]
            return semua_hasil

    def get_simsuka_group_sd(self,tglnya):
        #mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        mysql = """SELECT jns_trans,asal_dana, sum(amount), nm_bank, no_rek_bank, COUNT( * )  AS total_muncul FROM yudha_iuran_sukarela WHERE tgl_trans = %s and jns_trans='SD' group by no_rek_bank,amount,jns_trans,asal_dana,nm_bank;"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnst = res['jns_trans']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'jns_trans': jnst,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb,}
                semua_hasil += [hasil]
            return semua_hasil

    def get_simsuka_group_td(self,tglnya):
        #mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        mysql = """SELECT jns_trans,asal_dana, nm_bank, sum(amount), no_rek_bank, COUNT( * )  AS total_muncul FROM yudha_iuran_sukarela WHERE tgl_trans = %s and jns_trans='TD' group by jns_trans,asal_dana, nm_bank, no_rek_bank"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnst = res['jns_trans']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'jns_trans': jnst,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb,}
                semua_hasil += [hasil]
            return semua_hasil

    def get_tabungan_group_sd(self,tglnya):
        #mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        #mysql = """select b.name, a.no_rek_bank, sum(a.jml_tab), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id Where a.tgl_trans =%s AND a.jns_trans='SD' group by  a.no_rek_bank , b.name, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        mysql ="""select c.id, a.no_rek_bank, sum(a.jml_tab), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id INNER JOIN account_account c ON b.akun_coa=c.id Where a.tgl_trans =%s AND a.jns_trans='SD' group by  a.no_rek_bank , c.id, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jns_tab = res['id']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'id': jns_tab,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb,}
                semua_hasil += [hasil]
            return semua_hasil

    def get_tabungan_group_td(self, tglnya):
        # mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        # mysql = """select b.name, a.no_rek_bank, sum(a.jml_tab), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id Where a.tgl_trans =%s AND a.jns_trans='SD' group by  a.no_rek_bank , b.name, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        mysql = """select c.id, a.no_rek_bank, sum(a.jml_tab), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_tabungan a INNER JOIN yudha_master_jenis_tabungan b ON a.jenis_tabungan=b.id INNER JOIN account_account c ON b.akun_coa=c.id Where a.tgl_trans =%s AND a.jns_trans='TD' group by  a.no_rek_bank , c.id, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jns_tab = res['id']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'id': jns_tab,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb, }
                semua_hasil += [hasil]
            return semua_hasil

    def get_deposito_group_sd(self, tglnya):
        # mysql = """SELECT count(a.no_rek_bank) CASE  WHEN count(a.no_rek_bank) > 0 THEN sum(a,amount) ELSE a.mount  END AS jml_tab FROM yudha_iuran_pokok a WHERE a.tgl_trans=%s AND a.jns_trans='SD' ;"""
        mysql = """select c.id, a.no_rek_bank, sum(a.jml_depo), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_deposito a INNER JOIN yudha_master_jenis_deposito b ON a.jns_depo=b.id INNER JOIN account_account c ON b.akun_coa=c.id Where a.tgl_trans =%s AND a.jns_trans='SD' group by  a.no_rek_bank, c.id, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnsdepo = res['id']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'id': jnsdepo,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb, }
                semua_hasil += [hasil]
            return semua_hasil

    def get_deposito_group_td(self, tglnya):
        # mysql = """select c.id, a.no_rek_bank, sum(a.jml_depo), a.asal_dana, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_deposito a INNER JOIN yudha_master_jenis_deposito b ON a.jns_depo=b.id INNER JOIN account_account c ON b.akun_coa=c.id Where a.tgl_trans =%s AND a.jns_trans='TD' group by  a.no_rek_bank, c.id, a.asal_dana,a.nm_bank, a.no_rek_bank;"""
        mysql= """select d.id, a.no_rek_bank, sum(b.jml_depo), b.type_bayar, a.nm_bank,a.no_rek_bank, COUNT(*) as total_muncul from yudha_deposito a inner JOIN yudha_pencairan_deposito b on a.id=b.depo_id inner join
                  yudha_master_jenis_deposito c ON a.jns_depo=c.id INNER JOIN account_account d ON c.akun_coa=d.id Where a.tgl_trans =%s group by  a.no_rek_bank, d.id, b.type_bayar,a.nm_bank, a.no_rek_bank;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        hasil = {}
        semua_hasil = []
        if not result:
            return
        else:
            for res in result:
                jnsdepo = res['id']
                asl_dana = res['asal_dana']
                jmlduit = res['sum']
                totmun = res['total_muncul']
                norek = res['no_rek_bank']
                nmb = res['nm_bank']
                hasil = {'id': jnsdepo,
                         'sum': jmlduit,
                         'total_muncul': totmun,
                         'no_rek_bank': norek,
                         'asal_dana': asl_dana,
                         'nm_bank': nmb, }
                semua_hasil += [hasil]
            return semua_hasil

    def get_total_peminjaman(self, tglnya):
        sum_total=0
        for res in self.valpinjam_ids:
            sum_total += res['jml_pinjam']
        return sum_total

    def get_total_peminjaman_old(self, tglnya):
        mysql = """select sum(jml_pinjam) from yudha_peminjaman_dana where state='draft' and tgl_trans=%s;
            """
        self.env.cr.execute(mysql, (tglnya,))
        sum_dana = self.env.cr.fetchone()[0] or 0
        mysql = """select sum(jml_pinjam) from yudha_peminjaman_barang where state='draft' and tgl_trans=%s;
            """
        self.env.cr.execute(mysql, (tglnya,))
        sum_barang = self.env.cr.fetchone()[0] or 0
        mysql = """select sum(jml_pinjam) from yudha_peminjaman_konsumtif where state='draft' and tgl_trans=%s;
            """
        self.env.cr.execute(mysql, (tglnya,))
        sum_konsumtif = self.env.cr.fetchone()[0] or 0
        mysql = """select sum(jml_pinjam) from yudha_peminjaman_sembako where state='draft' and tgl_trans=%s;
            """
        self.env.cr.execute(mysql, (tglnya,))
        sum_sembako = self.env.cr.fetchone()[0] or 0
        mysql = """select sum(jml_pinjam) from yudha_peminjaman_syariah where state='draft' and tgl_trans=%s;
            """
        self.env.cr.execute(mysql, (tglnya,))
        sum_syariah = self.env.cr.fetchone()[0] or 0
        sum_total=sum_dana+sum_barang+sum_konsumtif+sum_sembako+sum_syariah
        return sum_total

    def get_total_pelunasan_peminjaman(self, tglnya):
        hasil = {}
        semua_hasil = []
        amountCS=0
        amountTF=0

        for res in self.vallunas_ids:
            if res['asal_dana']=='CS':
                amountCS += res['amount']
            elif res['asal_dana']=='TF':
                amountTF += res['amount']

        hasil = {'amountCS': amountCS,
                 'amountTF': amountTF,
                 }
        semua_hasil = [hasil]
        return semua_hasil


    def get_total_pelunasan_peminjaman_old(self, tglnya):
        hasil = {}
        semua_hasil = []
        asal_dana=0
        amountCS=0
        amountTF=0
        mysql = """select asal_dana,sum(amount) as amount from yudha_pelunasan_dana where 
                state='confirm' and doc_type='inbound' and date_pay=%s group by asal_dana;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        if result:
            for res in result:
                if res['asal_dana']=='CS':
                    amountCS += res['amount']
                elif res['asal_dana']=='TF':
                    amountTF += res['amount']
        mysql = """select asal_dana,sum(amount) as amount from yudha_pelunasan_barang where 
                state='confirm' and doc_type='inbound' and date_pay=%s group by asal_dana;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        if result:
            for res in result:
                if res['asal_dana']=='CS':
                    amountCS += res['amount']
                elif res['asal_dana']=='TF':
                    amountTF += res['amount']
        mysql = """select asal_dana,sum(amount) as amount from yudha_pelunasan_konsumtif where 
                state='confirm' and doc_type='inbound' and date_pay=%s group by asal_dana;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        if result:
            for res in result:
                if res['asal_dana']=='CS':
                    amountCS += res['amount']
                elif res['asal_dana']=='TF':
                    amountTF += res['amount']
        mysql = """select asal_dana,sum(amount) as amount from yudha_pelunasan_sembako where 
                state='confirm' and doc_type='inbound' and date_pay=%s group by asal_dana;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        if result:
            for res in result:
                if res['asal_dana']=='CS':
                    amountCS += res['amount']
                elif res['asal_dana']=='TF':
                    amountTF += res['amount']
        mysql = """select asal_dana,sum(amount) as amount from yudha_pelunasan_syariah where 
                state='confirm' and doc_type='inbound' and date_pay=%s group by asal_dana;
                """
        self.env.cr.execute(mysql, (tglnya,))
        result = self.env.cr.dictfetchall()
        if result:
            for res in result:
                if res['asal_dana']=='CS':
                    amountCS += res['amount']
                elif res['asal_dana']=='TF':
                    amountTF += res['amount']

        hasil = {'amountCS': amountCS,
                 'amountTF': amountTF,
                 }
        semua_hasil = [hasil]
        return semua_hasil

    
    def validate(self):
        if self.state == 'done':
            raise UserError((
                                'Error!\n'
                                'Tidak dapat memvalidasi data untuk No Document %s karena sudah di Validasi ') % (
                                self.no_val))
        accmov = self.env['account.move']

        acc_setor ={}
        acc_tarik = {}
        acc_item = []
        acc_item2 = []
        acc_line ={}
        acc_line1 = {}
        DATETIME_FORMAT = "%Y-%m-%d"
        timbang_date = datetime.strptime(self.tgl_val, DATETIME_FORMAT)
        tanggalan = timbang_date.strftime('%Y-%m-%d')
        mycomp = self._get_company_id()
        namaacc  = ''
        tahun = datetime.now().year
        lstjr=self.get_last_journal()
        lstjr += 1
        counter= 0000 + lstjr
        mycekval = accmov.search([('date', '=',tanggalan)])
        if mycekval:
            for allcekval in mycekval:
                if allcekval.ref =='Akumulasi penyetoran tabungan dan simpanan' or allcekval.ref =='Akumulasi penarikan tabungan dan simpanan':
                    raise UserError((
                                        'Error!\n'
                                        'Tidak dapat memvalidasi data untuk hari ini karena sudah pernah di validasi') )
        counter =str(lstjr+1)
        namaaccount='%s/%s/%s' % ('KOPKARTRNS',tahun,  counter)
        jid = self.env['account.journal'].search(
            [('name', '=', 'Unit Simpan Pinjam'), ('company_id', '=', mycomp)], limit=1)
        # print('line 645', jid.id)
        # print('line 746', mycomp)
        totbayar = 0
        acc_anna = self.env['account.analytic.account'].search(
            ['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', mycomp)],
            limit=1)
        totduitsetor = 0
        setortunaisimpok = 0
        totduitsetorsimpok = 0
        SDCount = 0
        tottranssimpok = 0
        datasimpok_sd = self.get_simpok_group_sd(tanggalan)
        if not datasimpok_sd is None:
            isSimpokSD ='Y'
            for allsimpok in datasimpok_sd:
                if allsimpok['asal_dana'] =='TF':
                    tottranssimpok += allsimpok['sum']
                    namaacc = 0
                    myjurnal = self.env['account.journal'].search([('id','=',allsimpok['no_rek_bank'])])
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', 'ilike', myjurnal.name), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': 'Transfer Simpanan Pokok',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': allsimpok['sum'],
                                'credit': 0}
                    acc_item.append((0, 0, acc_line))
                    acc_setor['line_ids'] = acc_item
                else:
                    setortunaisimpok += allsimpok['sum']
                totduitsetorsimpok += allsimpok['sum']
            namaacc = self.env['account.account'].search(
                ['&', ('name', '=', 'SIMPANAN POKOK ANGGOTA'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': namaacc.id,
                        'name': 'Simpanan Pokok',
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': totduitsetorsimpok}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
        else:
            isSimpokSD = 'N'
            SDCount = 0
            totduitsetorsimpok = 0

        TDCount = 0
        tariksimpok = 0
        totduittariksimpok = 0
        datasimpok_td = self.get_simpok_group_td(tanggalan)
        if not datasimpok_td is None:
            isSimpokTD ='Y'
            TDCount = 1
            for allsimpoktd in datasimpok_td:
                totduittariksimpok += allsimpoktd['sum']
            namaacc = self.env['account.account'].search(
                ['&', ('name', '=', 'SIMPANAN POKOK ANGGOTA'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': namaacc.id,
                        'name': 'Simpanan Pokok',
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': totduittariksimpok,
                        'credit': 0}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2
        else:
            isSimpokTD = 'N'
            TDCount = 0
            totduittariksimpok = 0

        setortunaisimsuka = 0
        totduitsetorsimsuka = 0
        isSimSukaSD = ''
        totbayarsimsimsuka = 0
        # acc_line = {}
        # acc_setor = {}
        # acc_item = []
        datasimsuka_sd = self.get_simsuka_group_sd(tanggalan)
        if not datasimsuka_sd is None:
            isSimSukaSD ='Y'
            SDCount = 3
            for allsimsuka in datasimsuka_sd:
                totduitsetorsimsuka += allsimsuka['sum']
                if allsimsuka['asal_dana'] =='TF':
                    namaacc = 0
                    myjurnal = self.env['account.journal'].search([('id','=',allsimsuka['no_rek_bank'])])
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', 'ilike', myjurnal.name), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': 'Transfer Simpanan Sukarela',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': allsimsuka['sum'],
                                'credit': 0}
                    acc_item.append((0, 0, acc_line))
                    acc_setor['line_ids'] = acc_item
                else:
                    setortunaisimsuka += allsimsuka['sum']
            namaacc = self.env['account.account'].search(
                ['&', ('name', '=', 'SIMPANAN SUKARELA ANGGOTA'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': namaacc.id,
                        'name': 'Simpanan Sukarela ',
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': 0,
                        'credit': totduitsetorsimsuka}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
        else:
            SDCount =  1
            isSimSukaSD = 'N'

        isSimSukaTD = ''
        totduittariksimsuka = 0
        tariksimsuka = 0
        datasimsuka_td = self.get_simsuka_group_td(tanggalan)
        if not datasimsuka_td is None:
            isSimSukaTD ='Y'
            TDCount = 2
            for allsimsukatd in datasimsuka_td:
                totduittariksimsuka += allsimsukatd['sum']
            namaacc = self.env['account.account'].search(
                ['&', ('name', '=', 'SIMPANAN SUKARELA ANGGOTA'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': namaacc.id,
                        'name': 'Simpanan  Sukarela',
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'company_id': mycomp,
                        'debit': totduittariksimsuka,
                        'credit': 0}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2
        else:
            isSimSukaTD = 'N'
            TDCount = 1
            totduittariksimsuka = 0

        setortunaitab = 0
        isTabSD = ''
        datatab_sd = self.get_tabungan_group_sd(tanggalan)
        if not datatab_sd is None:
            isTabSD ='Y'
            SDCount = 3
            for alltab in datatab_sd:
                if alltab['asal_dana'] =='TF':
                    namaacc = 0
                    myjurnal = self.env['account.journal'].search([('id','=',alltab['no_rek_bank'])])
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', 'ilike', myjurnal.name), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': 'Setoran Tabungan - Transfer',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': alltab['sum'],
                                'credit': 0}
                    acc_item.append((0, 0, acc_line))
                    acc_setor['line_ids'] = acc_item
                else:
                    setortunaitab += alltab['sum']
                namaacc = alltab['id']
                acc_line = {'account_id': namaacc,
                            'name': 'Setoran Tabungan - Tunai',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': alltab['sum']}
                acc_item.append((0, 0, acc_line))
                acc_setor['line_ids'] = acc_item
                #totduitsetorsimpok += alltab['sum']
                # namaacc = self.env['account.account'].search(
                #     ['&', ('name', '=ilike', alltab['name']), ('company_id', '=', mycomp)])

        else:
            isTabSD = 'N'
            SDCount = 2

        isTabTD = ''
        totduittariktab = 0
        datatab_td = self.get_tabungan_group_td(tanggalan)
        if not datatab_td is None:
            isTabTD = 'Y'
            TDCount = 3
            for alltabtd in datatab_td:
                totduittariktab += alltabtd['sum']
                namaacc = alltabtd['id']
                acc_line1 = {'account_id': namaacc,
                            'name': 'Tarikan Tabungan Tunai',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': alltabtd['sum'],
                            'credit': 0}
                acc_item2.append((0, 0, acc_line1))
                acc_tarik['line_ids'] = acc_item2
                # totduitsetorsimpok += alltab['sum']
                # namaacc = self.env['account.account'].search(
                #     ['&', ('name', '=ilike', alltab['name']), ('company_id', '=', mycomp)])

        else:
            TDCount = 2
            totduittariktab = 0

        #Notes by AK :
        # Untuk Setoran secara Transfer, customer harus melakukan transfer terlebih
        # dahulu baru dilakukan input transaksi
        # Journal yang terbentuk :
        #   Transfer : Bank Penerima USP di form pada COA di master deposito pada
        setortunaidepo = 0
        isDepoSD = ''
        datadepo_sd = self.get_deposito_group_sd(tanggalan)
        if not datadepo_sd is None:
            isDepoSD = 'Y'
            SDCount = 4
            for alldeposd in datadepo_sd:
                if alldeposd['asal_dana'] == 'TF':
                    namaacc = 0
                    myjurnal = self.env['account.journal'].search([('id', '=', alldeposd['no_rek_bank'])])
                    namaacc = self.env['account.account'].search(
                        ['&', ('name', 'ilike', myjurnal.name), ('company_id', '=', mycomp)])
                    acc_line = {'account_id': namaacc.id,
                                'name': 'Setoran Deposito - Transfer',
                                'analytic_account_id': acc_anna.id,
                                'analytic_tag_ids': '',
                                'company_id': mycomp,
                                'debit': alldeposd['sum'],
                                'credit': 0}
                    acc_item.append((0, 0, acc_line))
                    acc_setor['line_ids'] = acc_item
                else:
                    setortunaidepo += alldeposd['sum']
                namaacc = alldeposd['id']
                acc_line = {'account_id': namaacc,
                            'name': 'Setoran Deposito',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': alldeposd['sum']}
                acc_item.append((0, 0, acc_line))
                acc_setor['line_ids'] = acc_item

        else:
            isDepoSD = 'N'
            SDCount = 3

        # Subject edit by AK: Deposito saat ini hanya dikelola SD saja, sementara
        #   untuk pencairan deposito menggunakan table yudha_pencairan_deposito

        isDepoTD = ''
        totduittarikdepo =0
        datadepo_td = self.get_deposito_group_td(tanggalan)
        if not datadepo_td is None:
            isDepoTD = 'Y'
            TDCount = 4
            for alldepotd in datadepo_td:
                totduittarikdepo += alldepotd['sum']
                namaacc = alldepotd['id']
                acc_line1 = {'account_id': namaacc,
                            'name': 'Tarikan Deposito',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': alldepotd['sum'],
                            'credit': 0}
                acc_item2.append((0, 0, acc_line1))
                acc_tarik['line_ids'] = acc_item2
                # totduitsetorsimpok += alltab['sum']
                # namaacc = self.env['account.account'].search(
                #     ['&', ('name', '=ilike', alltab['name']), ('company_id', '=', mycomp)])

        else:
            isDepoTD = 'N'
            totduittarikdepo=0

        #add by Agus
        #subject utk ditambahkan peminjaman dan pelunasan pinjaman
        #total peminjaman
        #Journal : Piutang Pinjaman Anggota pada Kliring Pinjaman Anggota
        addJournal = ''
        if not acc_item:
            addJournal = 'Y'
        tot_pinjam = 0
        tot_pinjam = self.get_total_peminjaman(tanggalan)
        if tot_pinjam>0:
            debit_acc = self.env['account.account'].search([('name','=','PIUTANG PINJAMAN ANGGOTA'),('company_id','=',mycomp)]).id
            credit_acc = self.env['account.account'].search([('name','=','KLIRING PINJAMAN ANGGOTA'),('company_id','=',mycomp)]).id
            acc_line = {'account_id': debit_acc,
                         'name': 'Peminjaman',
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'company_id': mycomp,
                         'debit': tot_pinjam,
                         'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_line = {'account_id': credit_acc,
                         'name': 'Peminjaman',
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tot_pinjam}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item

        # total pelunasan peminjaman
        # Journal :
        #    Cash : Kas Simpan Pinjam pada Piutang Pinjaman Anggota
        #    Transfer : Kliring Pinjaman Anggota pada Piutang Pinjaman Anggota

        tot_lunas = 0
        data_lunas = self.get_total_pelunasan_peminjaman(tanggalan)
        if not data_lunas is None:
            amountCS = 0
            amountTF = 0
            for line in data_lunas:
                amountCS += line['amountCS']
                amountTF += line['amountTF']

            #    Cash : Kas Simpan Pinjam pada Piutang Pinjaman Anggota
            if amountCS > 0:
                debit_cash_acc = self.env['account.account'].search(
                    [('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)]).id
                credit_acc = self.env['account.account'].search(
                    [('name', '=', 'PIUTANG PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)]).id

                acc_line = {'account_id': debit_cash_acc,
                             'name': 'Pelunasan Pokok Pinjaman',
                             'analytic_account_id': acc_anna.id,
                             'analytic_tag_ids': '',
                             'company_id': mycomp,
                             'debit': amountCS,
                             'credit': 0}
                acc_item.append((0, 0, acc_line))
                acc_line = {'account_id': credit_acc,
                             'name': 'Pelunasan Pokok Pinjaman',
                             'analytic_account_id': acc_anna.id,
                             'analytic_tag_ids': '',
                             'company_id': mycomp,
                             'debit': 0,
                             'credit': amountCS}
                acc_item.append((0, 0, acc_line))
                acc_setor['line_ids'] = acc_item

            #    Transfer : Kliring Pinjaman Anggota pada Piutang Pinjaman Anggota
            if amountTF > 0:
                debit_trf_acc = self.env['account.account'].search(
                    [('name', '=', 'KLIRING PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)]).id
                credit_acc = self.env['account.account'].search(
                    [('name', '=', 'PIUTANG PINJAMAN ANGGOTA'), ('company_id', '=', mycomp)]).id
                acc_line = {'account_id': debit_trf_acc,
                             'name': 'Pelunasan Pokok Pinjaman',
                             'analytic_account_id': acc_anna.id,
                             'analytic_tag_ids': '',
                             'company_id': mycomp,
                             'debit': amountTF,
                             'credit': 0}
                acc_item.append((0, 0, acc_line))
                acc_line = {'account_id': credit_acc,
                             'name': 'Pelunasan Pokok Pinjaman',
                             'analytic_account_id': acc_anna.id,
                             'analytic_tag_ids': '',
                             'company_id': mycomp,
                             'debit': 0,
                             'credit': amountTF}
                acc_item.append((0, 0, acc_line))
                acc_setor['line_ids'] = acc_item
        if addJournal=='Y':
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        # end of edit

        if isSimSukaSD == 'Y' and isSimpokSD == 'Y' and isTabSD == 'Y' and isDepoSD == 'Y':
            totbayar = setortunaisimpok + setortunaisimsuka + setortunaitab + setortunaidepo
            acc_setor = {'date': fields.datetime.now(),
                          'journal_id': jid.id,
                          'company_id': mycomp,
                          'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                          'name': namaaccount}
            accid = self.env['account.account'].search(['&',('name', '=', 'KAS UNIT SIMPAN PINJAM'),('company_id','=',mycomp)])
            acc_line = {'account_id': int(accid),
                    'analytic_account_id': acc_anna.id,
                    'analytic_tag_ids': '',
                    'name': '',
                    'company_id': mycomp,
                    'debit': totbayar,
                    'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'Y' and isTabSD == 'Y' and isDepoSD == 'N':
        #elif SDCount == 3:
            if setortunaisimpok > 0 and setortunaisimsuka > 0 and setortunaitab >0 :
                totbayar = setortunaisimpok + setortunaisimsuka + setortunaitab
            elif setortunaisimpok > 0 and setortunaisimsuka > 0 and setortunaitab == 0 :
                totbayar = setortunaisimpok + setortunaisimsuka
            elif setortunaisimpok > 0 and setortunaisimsuka == 0 and setortunaitab > 0:
                totbayar = setortunaisimpok + setortunaitab
            elif setortunaisimpok == 0 and setortunaisimsuka > 0 and setortunaitab > 0:
                totbayar = setortunaisimsuka + setortunaitab
            elif setortunaisimpok == 0 and setortunaisimsuka == 0 and setortunaitab > 0:
                totbayar = setortunaitab
            elif setortunaisimpok == 0 and setortunaisimsuka > 0 and setortunaitab == 0:
                totbayar = setortunaisimsuka
            else:
                totbayar = setortunaisimpok
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            print('line 1133', acc_setor)
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'Y' and isTabSD == 'N' and isDepoSD == 'Y':
            if setortunaisimpok > 0 and setortunaisimsuka > 0 and setortunaidepo >0 :
                totbayar = setortunaisimpok + setortunaisimsuka + setortunaidepo
            elif setortunaisimpok > 0 and setortunaisimsuka > 0 and setortunaidepo == 0 :
                totbayar = setortunaisimpok + setortunaisimsuka
            elif setortunaisimpok > 0 and setortunaisimsuka == 0 and setortunaidepo > 0:
                totbayar = setortunaisimpok + setortunaidepo
            elif setortunaisimpok == 0 and setortunaisimsuka > 0 and setortunaidepo > 0:
                totbayar = setortunaisimsuka + setortunaidepo
            elif setortunaisimpok == 0 and setortunaisimsuka == 0 and setortunaidepo > 0:
                totbayar = setortunaidepo
            elif setortunaisimpok == 0 and setortunaisimsuka > 0 and setortunaidepo == 0:
                totbayar = setortunaisimsuka
            else:
                totbayar = setortunaisimpok
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'N' and isTabSD == 'Y' and isDepoSD == 'Y':
            totbayar = setortunaisimpok + setortunaisimsuka + setortunaitab + setortunaidepo
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'Y' and isTabSD == 'Y' and isDepoSD == 'Y':
            if setortunaisimpok > 0 and setortunaitab > 0 and setortunaidepo > 0:
                totbayar = setortunaisimpok + setortunaitab + setortunaidepo
            elif setortunaisimpok > 0 and setortunaitab > 0 and setortunaidepo == 0:
                totbayar = setortunaisimpok + setortunaitab
            elif setortunaisimpok > 0 and setortunaitab == 0 and setortunaidepo > 0:
                totbayar = setortunaisimpok + setortunaidepo
            elif setortunaisimpok == 0 and setortunaitab > 0 and setortunaidepo > 0:
                totbayar = setortunaitab + setortunaidepo
            elif setortunaisimpok == 0 and setortunaitab == 0 and setortunaidepo > 0:
                totbayar = setortunaidepo
            elif setortunaisimpok == 0 and setortunaitab > 0 and setortunaidepo == 0:
                totbayar = setortunaitab
            else:
                totbayar = setortunaisimpok
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'Y' and isTabSD == 'N' and isDepoSD == 'N':
            if setortunaisimpok > 0 and setortunaisimsuka > 0:
                totbayar = setortunaisimpok + setortunaisimsuka
            elif setortunaisimpok > 0 and setortunaisimsuka == 0 :
                totbayar = setortunaisimpok
            else:
                totbayar = setortunaisimsuka
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'N' and isTabSD == 'Y' and isDepoSD == 'N':
            if setortunaisimsuka > 0 and setortunaitab > 0:
                totbayar = setortunaisimsuka + setortunaitab
            elif setortunaisimpok > 0 and setortunaitab == 0 :
                totbayar = setortunaisimsuka
            else:
                totbayar = setortunaitab
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'Y' and isSimpokSD == 'N' and isTabSD == 'N' and isDepoSD == 'Y':
            if setortunaisimsuka > 0 and setortunaidepo > 0:
                totbayar = setortunaisimsuka + setortunaidepo
            elif setortunaisimsuka > 0 and setortunaidepo == 0 :
                totbayar = setortunaisimsuka
            else:
                totbayar = setortunaidepo
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'Y' and isTabSD == 'Y' and isDepoSD == 'N':
            if setortunaisimpok > 0 and setortunaitab > 0:
                totbayar = setortunaisimpok + setortunaitab
            elif setortunaisimpok > 0 and setortunaitab == 0 :
                totbayar = setortunaisimpok
            else:
                totbayar = setortunaitab
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'N' and isTabSD == 'Y' and isDepoSD == 'Y':
            if setortunaitab > 0 and setortunaidepo >0:
                totbayar = setortunaitab + setortunaidepo
            elif setortunaitab > 0 and setortunaidepo == 0 :
                totbayar = setortunaitab
            else:
                totbayar = setortunaidepo
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'N' and isTabSD == 'N' and isDepoSD == 'Y':
            if setortunaidepo > 0:
                totbayar = setortunaidepo
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'N' and isTabSD == 'Y' and isDepoSD == 'N':
            if setortunaitab > 0:
                totbayar = setortunaitab
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        elif isSimSukaSD == 'N' and isSimpokSD == 'Y' and isTabSD == 'N' and isDepoSD == 'N':
            if setortunaisimpok > 0:
                totbayar = setortunaisimpok
            acc_setor = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                         'name': namaaccount}
            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line = {'account_id': int(accid),
                        'analytic_account_id': acc_anna.id,
                        'analytic_tag_ids': '',
                        'name': '',
                        'company_id': mycomp,
                        'debit': totbayar,
                        'credit': 0}
            acc_item.append((0, 0, acc_line))
            acc_setor['line_ids'] = acc_item
            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
            buat_jurnal_setor.post()
        else:
            if setortunaisimpok > 0:
                totbayar = setortunaisimsuka

                acc_setor = {'date': fields.datetime.now(),
                             'journal_id': jid.id,
                             'company_id': mycomp,
                             'ref': 'Akumulasi penyetoran tabungan dan simpanan',
                             'name': namaaccount}
                accid = self.env['account.account'].search(
                    ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
                acc_line = {'account_id': int(accid),
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'name': '',
                            'company_id': mycomp,
                            'debit': totbayar,
                            'credit': 0}
                acc_item.append((0, 0, acc_line))
                acc_setor['line_ids'] = acc_item
                buat_jurnal_setor = self.env['account.move'].create(acc_setor)
                buat_jurnal_setor.post()

        if isSimSukaTD == 'Y' and isSimpokTD == 'Y' and isTabTD == 'Y' and isDepoTD == 'Y':
           tottarik = totduittariksimsuka + totduittariksimpok + totduittariktab +totduittarikdepo
           acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

           accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
           acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
           acc_item2.append((0, 0, acc_line1))
           acc_tarik['line_ids'] = acc_item2
           print('line 1462', acc_tarik)
           buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
           buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'Y' and isTabTD == 'Y' and isDepoTD == 'N':
           tottarik = totduittariksimsuka + totduittariksimpok + totduittariktab
           acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

           accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
           acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
           acc_item2.append((0, 0, acc_line1))
           acc_tarik['line_ids'] = acc_item2

           buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
           buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'Y' and isTabTD == 'N' and isDepoTD == 'Y':
            tottarik = totduittariksimsuka + totduittariksimpok + totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'N' and isTabTD == 'Y' and isDepoTD == 'Y':
            tottarik =  totduittariksimsuka + totduittariktab + totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'Y' and isTabTD == 'Y' and  isDepoTD == 'Y':
            tottarik = totduittariksimpok + totduittariktab + totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'Y' and isTabTD == 'N' and isDepoTD == 'N':
            tottarik = totduittariksimpok + totduittariksimsuka
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'N' and isTabTD == 'Y' and isDepoTD == 'N':
            tottarik =  totduittariksimsuka + totduittariktab
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'N' and isTabTD == 'N' and isDepoTD == 'Y':
            tottarik =  totduittariksimsuka + totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'Y' and isTabTD == 'Y' and isDepoTD == 'N':
            tottarik = totduittariksimpok  + totduittariktab
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'N' and isTabTD == 'Y' and isDepoTD == 'Y':
            tottarik = totduittariktab + totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'N' and isTabTD == 'N' and isDepoTD == 'Y':
            tottarik =  totduittarikdepo
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'N' and isTabTD == 'Y' and isDepoTD == 'N':
            tottarik = totduittariktab
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'N' and isSimpokTD == 'Y' and isTabTD == 'N' and isDepoTD == 'N':
            tottarik = totduittariksimpok
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()
        elif isSimSukaTD == 'Y' and isSimpokTD == 'N' and isTabTD == 'N' and isDepoTD == 'N':
            tottarik = totduittariksimsuka
            acc_tarik = {'date': fields.datetime.now(),
                         'journal_id': jid.id,
                         'company_id': mycomp,
                         'ref': 'Akumulasi penarikan tabungan dan simpanan',
                         'name': namaaccount}

            accid = self.env['account.account'].search(
                ['&', ('name', '=', 'KAS UNIT SIMPAN PINJAM'), ('company_id', '=', mycomp)])
            acc_line1 = {'account_id': int(accid),
                         'analytic_account_id': acc_anna.id,
                         'analytic_tag_ids': '',
                         'name': '',
                         'company_id': mycomp,
                         'debit': 0,
                         'credit': tottarik}
            acc_item2.append((0, 0, acc_line1))
            acc_tarik['line_ids'] = acc_item2

            buat_jurnal_tarik = self.env['account.move'].create(acc_tarik)
            buat_jurnal_tarik.post()

        for alldatasimpok in self.valsimpok_ids:
            if alldatasimpok.jns_trans =='SD':
                if alldatasimpok.no_trans != '':
                    self._update_setor_status(alldatasimpok.no_trans,buat_jurnal_setor.id)
                    myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                    if myval:
                        mysimpok = self.env['yudha.validasi.simpanan.pokok'].search([('valsimpok_id', '=', myval.id)])
                        if mysimpok:
                            for allsimpok in mysimpok:
                                allsimpok.write({'no_accmove': buat_jurnal_setor.id})
            else:
                if alldatasimpok.no_trans != '':
                    self._update_tarik_status(alldatasimpok.no_trans, buat_jurnal_tarik.id)
                    myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                    if myval:
                        mysimpok = self.env['yudha.validasi.simpanan.pokok'].search([('valsimpok_id', '=', myval.id)])
                        if mysimpok:
                            for allsimpok in mysimpok:
                                allsimpok.write({'no_accmove': buat_jurnal_tarik.id})
        for alldatasimsuka in self.valsimsuka_ids:
            if alldatasimsuka.jns_trans =='SD':
                if alldatasimsuka.no_trans != '':
                   self._update_setor_status(alldatasimsuka.no_trans,buat_jurnal_setor.id)
                   myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                   if myval:
                       mysim_suka = self.env['yudha.validasi.simpanan.sukarela'].search([('valsimsuka_id', '=', myval.id)])
                       if mysim_suka:
                           for allsim_suka in mysim_suka:
                               allsim_suka.write({'no_accmove': buat_jurnal_setor.id})
            else:
                if alldatasimsuka.no_trans != '':
                   self._update_tarik_status(alldatasimsuka.no_trans,buat_jurnal_tarik.id)
                   myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                   if myval:
                       mysim_suka = self.env['yudha.validasi.simpanan.sukarela'].search([('valsimsuka_id', '=', myval.id)])
                       if mysim_suka:
                           for allsim_suka in mysim_suka:
                               allsim_suka.write({'no_accmove': buat_jurnal_tarik.id})

        for alldatatab in self.valtab_ids:
            if alldatatab.jns_trans == 'SD':
               if alldatatab.no_trans != '':
                  self._update_setor_status(alldatatab.no_trans,buat_jurnal_setor.id)
                  myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                  if myval:
                     mydatatab = self.env['yudha.validasi.tabungan'].search([('valtab_id', '=', myval.id)])
                     if mydatatab:
                        for alltab in mydatatab:
                            alltab.write({'no_accmove': buat_jurnal_setor.id})
            else:
                if alldatatab.no_trans != '':
                   self._update_tarik_status(alldatatab.no_trans,buat_jurnal_tarik.id)
                   myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                   if myval:
                       mydatatab = self.env['yudha.validasi.tabungan'].search([('valtab_id', '=', myval.id)])
                       if mydatatab:
                           for alltab in mydatatab:
                               alltab.write({'no_accmove': buat_jurnal_tarik.id})
        for alldatadepo in self.valdepo_ids:
            if alldatadepo.jns_trans == 'SD':
               if alldatadepo.no_trans != '':
                  self._update_setor_status(alldatadepo.no_trans,buat_jurnal_setor.id)
                  myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                  if myval:
                      mydatadepo = self.env['yudha.validasi.deposito'].search([('valdepo_id', '=', myval.id)])
                      if mydatadepo:
                            for all_depos in mydatadepo:
                                all_depos.write({'no_accmove': buat_jurnal_setor.id})
            else:
                #Update status deposito ke payment untuk type Transfer
               if alldatadepo.transfer>0:
                   if alldatadepo.jns_trans=='TD':
                       depo_obj=self.env['yudha.deposito'].search([('no_trans','=',alldatadepo.no_trans)])
                       if depo_obj:
                           depo_obj.write({'state': 'payment'})
               if alldatadepo.no_trans != '':
                  self._update_tarik_status(alldatadepo.no_trans,buat_jurnal_tarik.id)
                  myval = self.env['yudha.validasi.harian'].search([('no_val', '=', self.no_val)])
                  if myval:
                      mydatadepo = self.env['yudha.validasi.deposito'].search([('valdepo_id', '=', myval.id)])
                      if mydatadepo:
                            for all_depos in mydatadepo:
                                all_depos.write({'no_accmove': buat_jurnal_tarik.id})

        #update balance res.partner -- Add by Agus
        #Peminjaman
        if self.valpinjam_ids:
            for pjm in self.valpinjam_ids:
                partner_obj = self.env['res.partner'].search([('id', '=', pjm.partner_id.id)])
                if pjm['nm_trans']=='Peminjaman Dana':
                    partner_obj.write({'pinj_dana':partner_obj.pinj_dana+pjm['jml_pinjam']})
                elif pjm['nm_trans']=='Peminjaman Barang':
                    partner_obj.write({'pinj_barang':partner_obj.pinj_barang+pjm['jml_pinjam']})
                elif pjm['nm_trans']=='Peminjaman Konsumtif':
                    partner_obj.write({'pinj_konsumtif':partner_obj.pinj_konsumtif+pjm['jml_pinjam']})
                elif pjm['nm_trans']=='Peminjaman Sembako':
                    partner_obj.write({'pinj_sembako':partner_obj.pinj_sembako+pjm['jml_pinjam']})
                elif pjm['nm_trans']=='Peminjaman Syariah':
                    partner_obj.write({'pinj_syariah':partner_obj.pinj_syariah+pjm['jml_pinjam']})
        #Pelunasan
        if self.vallunas_ids:
            for lns in self.vallunas_ids:
                partner_obj = self.env['res.partner'].search([('id', '=', lns.partner_id.id)])
                if lns['payment_type']=='dana':
                    partner_obj.write({'pinj_dana':partner_obj.pinj_dana-lns['amount']})
                elif lns['payment_type']=='barang':
                    partner_obj.write({'pinj_barang':partner_obj.pinj_barang-lns['amount']})
                elif lns['payment_type']=='konsumtif':
                    partner_obj.write({'pinj_konsumtif':partner_obj.pinj_konsumtif-lns['amount']})
                elif lns['payment_type']=='sembako':
                    partner_obj.write({'pinj_sembako':partner_obj.pinj_sembako-lns['amount']})
                elif lns['payment_type']=='syariah':
                    partner_obj.write({'pinj_syariah':partner_obj.pinj_syariah-lns['amount']})

        #update detail pinjaman
        dana_obj=self.env['yudha.peminjaman.dana'].search([('tgl_trans','=',tanggalan)])
        if dana_obj:
            for dn in dana_obj:
                dn.write({'state':'valid','valid_harian':self.id})
                detail_dana_obj = self.env['yudha.peminjaman.dana.details'].search([('loan_id', '=', dn.id)])
                if detail_dana_obj:
                    detail_dana_obj.write({'state':'valid','valid_harian':self.id})
        barang_obj=self.env['yudha.peminjaman.barang'].search([('tgl_trans','=',tanggalan)])
        if barang_obj:
            for br in barang_obj:
                br.write({'state':'valid','valid_harian':self.id})
                detail_barang_obj = self.env['yudha.peminjaman.barang.details'].search([('loan_id', '=', br.id)])
                if detail_barang_obj:
                    detail_barang_obj.write({'state':'valid','valid_harian':self.id})

        konsumtif_obj=self.env['yudha.peminjaman.konsumtif'].search([('tgl_trans','=',tanggalan)])
        if konsumtif_obj:
            for br in konsumtif_obj:
                br.write({'state':'valid','no_accmove':buat_jurnal_setor.id,'valid_harian':self.id})
                detail_konsumtif_obj = self.env['yudha.peminjaman.konsumtif.details'].search([('loan_id', '=', br.id)])
                if detail_konsumtif_obj:
                    detail_konsumtif_obj.write({'state':'valid','valid_harian': self.id})

        sembako_obj=self.env['yudha.peminjaman.sembako'].search([('tgl_trans','=',tanggalan)])
        if sembako_obj:
            for br in sembako_obj:
                br.write({'state':'valid','valid_harian':self.id})
                detail_sembako_obj = self.env['yudha.peminjaman.sembako.details'].search([('loan_id', '=', br.id)])
                if detail_sembako_obj:
                    detail_sembako_obj.write({'state':'valid','valid_harian': self.id})

        syariah_obj=self.env['yudha.peminjaman.syariah'].search([('tgl_trans','=',tanggalan)])
        if syariah_obj:
            for br in syariah_obj:
                br.write({'state':'valid','valid_harian':self.id})
                detail_syariah_obj = self.env['yudha.peminjaman.syariah.details'].search([('loan_id', '=', br.id)])
                if detail_syariah_obj:
                    detail_syariah_obj.write({'state':'valid','valid_harian': self.id})

        #update detail pelunasan
        pelunasan_dana_obj = self.env['yudha.pelunasan.dana'].search([('date_pay', '=', tanggalan)])
        if pelunasan_dana_obj:
            pelunasan_dana_obj.write({'state': 'valid'})
        pelunasan_barang_obj = self.env['yudha.pelunasan.barang'].search([('date_pay', '=', tanggalan)])
        if pelunasan_barang_obj:
            pelunasan_barang_obj.write({'state': 'valid'})
        pelunasan_konsumtif_obj = self.env['yudha.pelunasan.konsumtif'].search([('date_pay', '=', tanggalan)])
        if pelunasan_konsumtif_obj:
            pelunasan_konsumtif_obj.write({'state': 'valid'})
        pelunasan_sembako_obj = self.env['yudha.pelunasan.sembako'].search([('date_pay', '=', tanggalan)])
        if pelunasan_sembako_obj:
            pelunasan_sembako_obj.write({'state': 'valid'})
        pelunasan_syariah_obj = self.env['yudha.pelunasan.syariah'].search([('date_pay', '=', tanggalan)])
        if pelunasan_syariah_obj:
            pelunasan_syariah_obj.write({'state': 'valid'})

        self.write({'state':'done'})


class yudha_validasi_simpanan_pokok(models.Model):
    _name = 'yudha.validasi.simpanan.pokok'

    valsimpok_id = fields.Many2one('yudha.validasi.harian', string="Validasi Simpanan Pokok Details", required=False,store=True,index=True )
    no_trans = fields.Char(size=100, string='No. Transaksi')
    no_accmove = fields.Many2one('account.move', string='No Journal')
    tunai = fields.Float('Transaksi Tunai', digits=(19, 2), default=0, required=True)
    transfer = fields.Float('Transaksi Transfer', digits=(19, 2), default=0, required=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi', help='Jenis Transaksi')
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    atas_nama = fields.Char(size=100, string='Atas Nama')
    no_rek = fields.Many2one('account.journal', string='No Rekening USP', required=False)


class yudha_validasi_simpanan_sukarela(models.Model):
    _name = 'yudha.validasi.simpanan.sukarela'

    valsimsuka_id = fields.Many2one('yudha.validasi.harian', string="Validasi Simpanan Sukarela Details", required=False,store=True,index=True )
    no_trans = fields.Char(size=100, string='No. Transaksi')
    no_accmove = fields.Many2one('account.move', string='No Journal')
    tunai = fields.Float('Transaksi Tunai', digits=(19, 2), default=0, required=True)
    transfer = fields.Float('Transaksi Transfer', digits=(19, 2), default=0, required=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi', help='Jenis Transaksi')
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    atas_nama = fields.Char(size=100, string='Atas Nama')
    no_rek = fields.Many2one('account.journal', string='No Rekening USP', required=False)

class yudha_validasi_tabungan(models.Model):
    _name = 'yudha.validasi.tabungan'

    valtab_id = fields.Many2one('yudha.validasi.harian', string="Validasi Tabungan Details", required=False,store=True,index=True )
    no_trans = fields.Char(size=100, string='No. Transaksi')
    jns_tab = fields.Many2one('yudha.master.jenis.tabungan',string='Jenis Tabungan',index = True )
    no_accmove = fields.Many2one('account.move', string='No Journal')
    tunai = fields.Float('Transaksi Tunai', digits=(19, 2), default=0, required=True)
    transfer = fields.Float('Transaksi Transfer', digits=(19, 2), default=0, required=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi', help='Jenis Transaksi')
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    atas_nama = fields.Char(size=100, string='Atas Nama')
    no_rek = fields.Many2one('account.journal', string='No Rekening USP', required=False)


class yudha_validasi_deposito(models.Model):
    _name = 'yudha.validasi.deposito'

    valdepo_id = fields.Many2one('yudha.validasi.harian', string="Validasi Deposito Details", required=False,store=True,index=True )
    no_trans = fields.Char(size=100, string='No. Transaksi')
    no_accmove = fields.Many2one('account.move', string='No Journal')
    tunai = fields.Float('Transaksi Tunai', digits=(19, 2), default=0, required=True)
    transfer = fields.Float('Transaksi Transfer', digits=(19, 2), default=0, required=True)
    jns_trans = fields.Selection([('TD', 'Tarikan Dana'), ('SD', 'Setoran Dana')], string='Jenis Transaksi', help='Jenis Transaksi')
    no_rek_agt = fields.Char(size=100, string='No. Rekening Anggota')
    nm_bank = fields.Char(size=100, string='Nama Bank')
    atas_nama = fields.Char(size=100, string='Atas Nama')
    no_rek = fields.Many2one('account.journal', string='No Rekening USP', required=False)
    jns_depo = fields.Many2one('yudha.master.jenis.deposito', string='Jenis Deposito', required=True)

class yudha_validasi_pinjaman(models.Model):
    _name = 'yudha.validasi.pinjaman'

    valid_id = fields.Many2one('yudha.validasi.harian', string="Validasi Pinjaman Details", required=False,store=True,index=True )
    docnum = fields.Char(size=100, string='No. Transaksi', readonly=False)
    tgl_trans = fields.Date(string='Tanggal', required=False, default=lambda self: time.strftime("%Y-%m-%d"))
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,
                                 domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=False)
    jml_pinjam = fields.Float('Jumlah Pinjaman', digits=(19, 2), default=0, required=True)
    keterangan = fields.Char(size=100, string='Keterangan')
    nm_trans = fields.Char(size=100, string='Nama Transaksi', readonly=False)

class yudha_validasi_pelunasan_pinjaman(models.Model):
    _name = 'yudha.validasi.pelunasan.pinjaman'

    valid_id = fields.Many2one('yudha.validasi.harian', string="Validasi Pelunasan Pinjaman Details", required=False,store=True,index=True )
    date_pay = fields.Date(string='Tanggal Payment', required=False,default=False)  # , default=lambda self: time.strftime("%Y-%m-%d"))
    doc_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], string='Type', default='inbound')
    asal_dana = fields.Selection([('CS', 'Tunai'), ('TF', 'Transfer')], string='Sumber Dana', help='Sumber Dana',required=True)
    partner_id = fields.Many2one('res.partner', string='Nama Anggota', required=True, index=True,domain="[('category_id', '=', 'Anggota')]")
    no_agt = fields.Char(size=100, string='Nomer Anggota', readonly=False)
    loan_id = fields.Many2one(comodel_name="yudha.peminjaman.dana", inverse_name='id', string="Loan Id", required=False,default=False)
    date_loan = fields.Date(string='Tanggal Pinjam', required=False, default=False)
    amount = fields.Float('Jumlah', digits=(16, 2), default=0)
    payment_type = fields.Selection([('dana', 'Pinjaman Dana'), ('konsumtif', 'Pinjaman Konsumtif'), ('barang', 'Pinjaman Barang'), ('sembako', 'Pinjaman Sembako'), ('syariah', 'Pinjaman Syariah')], string='Payment Type')
