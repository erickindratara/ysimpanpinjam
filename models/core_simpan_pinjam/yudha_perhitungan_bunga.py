# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from  odoo.exceptions import UserError,ValidationError
import time
from datetime import date
from datetime import timedelta
from datetime import datetime

class yudha_perhitungan_bunga(models.Model):
    _name = "yudha.perhitungan.bunga"

    # date_proses = fields.Date(string="Date Process")
    # bulan = fields.Integer(string="Bulan")
    # tahun = fields.Integer(string="Tahun")
    # status = fields.Boolean(string="Status")

    
    def perhitungan_bunga_tabungan(self):
        #perhitungan bunga tabungan
        now = time.localtime()
        lastdate = date(now.tm_year, now.tm_mon, 1) - timedelta(1)
        firstdate = lastdate.replace(day=1)
        nb_of_days = int(lastdate.strftime('%d'))
        bulan = lastdate.strftime('%m')
        tahun = lastdate.strftime('%Y')

        tab_obj = self.env['yudha.tabungan']
        tab_check = tab_obj.search([('code_trans', '=', 'BNT'), ('tgl_trans', '=', lastdate)])
        if not tab_check:
            sql_query="""select distinct partner_id, no_agt from yudha_tabungan
                """
            self.env.cr.execute(sql_query,)
            result = self.env.cr.dictfetchall()
            if not result:
                return
            else:
                for res in result:
                    partner_id=res['partner_id']
                    no_agt=res['no_agt']
                    sql_query = """select distinct jenis_tabungan from yudha_tabungan
                        where partner_id=%s and tgl_trans between %s and %s
                        """
                    self.env.cr.execute(sql_query,(partner_id,firstdate,lastdate,))
                    res_jtab = self.env.cr.dictfetchall()
                    if res_jtab:
                        for jtab in res_jtab:
                            jenis_tabungan=jtab['jenis_tabungan']
                            biaya_admin=self.env['yudha.master.jenis.tabungan'].search([('id','=',jenis_tabungan)]).biaya_admin
                            sql_query = """select tgl_trans,balance_awal,balance_akhir from yudha_tabungan
                                where partner_id=%s and jenis_tabungan=%s and tgl_trans between %s and %s order by tgl_trans
                                """
                            self.env.cr.execute(sql_query,(partner_id,jenis_tabungan,firstdate,lastdate,))
                            res_tab = self.env.cr.dictfetchall()
                            trans_date=datetime.combine(firstdate, datetime.min.time())
                            saldo_bulanan=0
                            line=0
                            for tab in res_tab:
                                if line==0:
                                    saldo_akhir=tab['balance_awal']
                                    line=1
                                trans_date2=tab['tgl_trans']
                                trans_date2= datetime.strptime(trans_date2, '%Y-%m-%d')
                                ndays=abs((trans_date2 - trans_date).days)
                                saldo_bulanan += saldo_akhir*ndays
                                saldo_akhir = tab['balance_akhir']
                                balance_awal = saldo_akhir
                                trans_date=trans_date2

                            trans_date2 = datetime.combine(lastdate, datetime.min.time())
                            ndays = abs((trans_date2 - trans_date).days)
                            saldo_bulanan += saldo_akhir * ndays

                            #cari bunga tabungan
                            sql_query = """select rate_tab from yudha_rate_tabungan where tab_id=%s and tgl_input<=%s order 
                                by tgl_input desc limit 1
                                """
                            self.env.cr.execute(sql_query,(jenis_tabungan,lastdate,))
                            try:
                                bunga_tabungan = self.env.cr.fetchone()[0] or 0.0
                            except:
                                bunga_tabungan=0

                            # total_bunga=round((saldo_bulanan)*((bunga_tabungan/100)/365),2)
                            # pajak_bunga = round((10 / 100) * total_bunga, 2)

                            total_bunga=(saldo_bulanan)*((bunga_tabungan/100)/365)
                            pajak_bunga=(10/100)*total_bunga
                            balance_akhir=balance_awal+total_bunga
                            lastdate = datetime.combine(lastdate, datetime.min.time())
                            tgl_trans=datetime.strftime(lastdate, '%Y-%m-%d')
                            jml_bunga=total_bunga-pajak_bunga

                            tab_obj.create({
                                'tgl_trans': tgl_trans,
                                'jns_trans': 'SD',
                                'keterangan': 'Bunga Tabungan',
                                'partner_id': partner_id,
                                'no_agt': no_agt,
                                'jenis_tabungan': jenis_tabungan,
                                'jml_tab': total_bunga,
                                'balance_awal_view': balance_awal,
                                'balance_awal': balance_awal,
                                'credit': total_bunga,
                                'balance_akhir_view': balance_akhir,
                                'balance_akhir': balance_akhir,
                                'code_trans': 'BNT',
                                'state': 'done',
                                })
                            balance_awal=balance_akhir
                            balance_akhir=balance_awal-pajak_bunga
                            tab_obj.create({
                                'tgl_trans': tgl_trans,
                                'jns_trans': 'TD',
                                'keterangan': 'Pajak Bunga Tabungan',
                                'partner_id': partner_id,
                                'no_agt': no_agt,
                                'jenis_tabungan': jenis_tabungan,
                                'jml_tab': pajak_bunga,
                                'balance_awal_view': balance_awal,
                                'balance_awal': balance_awal,
                                'debit': pajak_bunga,
                                'balance_akhir_view': balance_akhir,
                                'balance_akhir': balance_akhir,
                                'code_trans': 'PJK',
                                'state': 'done',
                            })
                            balance_awal = balance_akhir
                            balance_akhir = balance_awal - biaya_admin
                            tab_obj.create({
                                'tgl_trans': tgl_trans,
                                'jns_trans': 'TD',
                                'keterangan': 'Biaya Admin Tabungan',
                                'partner_id': partner_id,
                                'no_agt': no_agt,
                                'jenis_tabungan': jenis_tabungan,
                                'jml_tab': biaya_admin,
                                'balance_awal_view': balance_awal,
                                'balance_awal': balance_awal,
                                'debit': biaya_admin,
                                'balance_akhir_view': balance_akhir,
                                'balance_akhir': balance_akhir,
                                'code_trans': 'ADM',
                                'state': 'done',
                            })
                            # buat journal move
                            settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)
                            journal_id = settings_obj.journal_id_tab.id
                            mycomp = self._get_company_id()
                            acc_anna = self.env['account.analytic.account'].search(
                                ['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', mycomp)],
                                limit=1)
                            tab_obj = self.env['yudha.master.jenis.tabungan'].search([('id', '=', jenis_tabungan)], limit=1)
                            acc_item = []
                            acc_line = {}
                            acc_line = {'account_id': settings_obj.coa_tab_bebanjasa.id,
                                        'name': 'Beban Bunga Tabungan',
                                        'analytic_account_id': acc_anna.id,
                                        'analytic_tag_ids': '',
                                        'company_id': mycomp,
                                        'debit': total_bunga,
                                        'credit': 0}
                            acc_item.append((0, 0, acc_line))
                            acc_line = {'account_id': tab_obj.akun_coa.id,
                                        'name': 'Bunga Tabungan',
                                        'analytic_account_id': acc_anna.id,
                                        'analytic_tag_ids': '',
                                        'company_id': mycomp,
                                        'debit': 0,
                                        'credit': jml_bunga}
                            acc_item.append((0, 0, acc_line))
                            acc_line = {'account_id': settings_obj.coa_tab_pajak.id,
                                        'name': 'Pajak Bunga Tabungan',
                                        'analytic_account_id': acc_anna.id,
                                        'analytic_tag_ids': '',
                                        'company_id': mycomp,
                                        'debit': 0,
                                        'credit': pajak_bunga}
                            acc_item.append((0, 0, acc_line))
                            acc_line = {'account_id': tab_obj.akun_coa.id,
                                        'name': 'Biaya Admin Tabungan',
                                        'analytic_account_id': acc_anna.id,
                                        'analytic_tag_ids': '',
                                        'company_id': mycomp,
                                        'debit': biaya_admin,
                                        'credit': 0}
                            acc_item.append((0, 0, acc_line))
                            acc_line = {'account_id': settings_obj.coa_tab_admin.id,
                                        'name': 'Biaya Admin Tabungan',
                                        'analytic_account_id': acc_anna.id,
                                        'analytic_tag_ids': '',
                                        'company_id': mycomp,
                                        'debit': 0,
                                        'credit': biaya_admin}
                            acc_item.append((0, 0, acc_line))
                            acc_setor = {}
                            lstjr = self.get_last_journal()
                            lstjr += 1
                            counter = str(lstjr + 1)
                            namaaccount = '%s/%s/%s' % ('KOPKARTRNS', tahun, counter)
                            acc_setor = {'date': tgl_trans,
                                         'journal_id': journal_id,
                                         'company_id': mycomp,
                                         'ref': 'Bunga Tabungan',
                                         'name': namaaccount}
                            acc_setor['line_ids'] = acc_item
                            buat_jurnal_setor = self.env['account.move'].create(acc_setor)
                            buat_jurnal_setor.post()

    #perhitungan bunga deposito menggunakan plan detail di module deposito
    
    def perhitungan_bunga_deposito(self):
        #perhitungan bunga deposito
        today = datetime.now().strftime("%Y-%m-%d")
        tahun = datetime.now().strftime("%Y")

        #check deposito yang jatuh tempo
        sql_query="""
            select a.id,a.docnum,b.date_trans,a.partner_id,a.no_agt,a.no_rek_agt,a.atasnama,a.nm_bank,a.bayar_bunga,a.no_rekening,a.nama_rekening,
            b.bulan_ke,b.date_trans,b.jml_bunga,b.jml_pajak,b.rencana_bayar from yudha_deposito a inner join yudha_deposito_details b
            on a.id=b.depo_id where a.state='deposit' and b.description='Bunga Deposito' and b.date_trans=%s
            """
        self.env.cr.execute(sql_query,(today,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            for res in result:
                bayar_bunga = res['bayar_bunga']
                no_rekening = res['no_rekening']
                nama_rekening = res['nama_rekening']
                jml_bunga = res['jml_bunga']
                jml_pajak = res['jml_pajak']
                rencana_bayar = res['rencana_bayar']
                partner_id = res['partner_id']
                no_agt = res['no_agt']
                no_rek_agt = res['no_rek_agt']
                atasnama = res['atasnama']
                nm_bank = res['nm_bank']
                depo_id = res['id']
                docnum = res['docnum']
                no_agt = res['no_agt']
                no_rek_agt = res['no_rek_agt']
                date_trans = res['date_trans']
                bulan_ke = res['bulan_ke']
                settings_obj = self.env['yudha.settings'].search([('code', '=', 'settings')], limit=1)

                if bayar_bunga=='transfer':
                    depo_obj = self.env['yudha.deposito.details.transfer']
                    depo_obj.create({
                        'depo_id': depo_id,
                        'docnum': docnum,
                        'partner_id': partner_id,
                        'no_agt': no_agt,
                        'no_rek_agt': no_rek_agt,
                        'atasnama': atasnama,
                        'nm_bank': nm_bank,
                        'bulan_ke': bulan_ke,
                        'date_trans': date_trans,
                        'bayar_bunga': bayar_bunga,
                        'jml_bunga': jml_bunga,
                        'jml_pajak': jml_pajak,
                        'rencana_bayar': rencana_bayar,
                    })
                else:
                    #buat transaksi ke tabungan
                    jenis_tabungan = settings_obj.jenis_tabungan.id
                    sql_query = """select sum(credit-debit) as balance_awal from yudha_tabungan where no_rekening=%s and partner_id=%s and jenis_tabungan=%s; """
                    self.env.cr.execute(sql_query, (no_rekening, partner_id, jenis_tabungan,))
                    balance_awal = self.env.cr.fetchone()[0] or 0.0
                    balance_akhir= balance_awal+rencana_bayar
                    tab_obj = self.env['yudha.tabungan']
                    tab_obj.create({
                        'tgl_trans': date_trans,
                        'jns_trans': 'SD',
                        'keterangan': 'Bunga Deposito',
                        'partner_id': partner_id,
                        'no_agt': no_agt,
                        'jenis_tabungan': jenis_tabungan,
                        'no_rekening': no_rekening,
                        'nama_rekening': nama_rekening,
                        'jml_tab': bayar_bunga,
                        'balance_awal_view': balance_awal,
                        'balance_awal': balance_awal,
                        'credit': rencana_bayar,
                        'balance_akhir_view': balance_akhir,
                        'balance_akhir': balance_akhir,
                        'code_trans': 'BND',
                        'state': 'done',
                    })
                    balance_awal = balance_akhir
                    balance_akhir = balance_awal - jml_pajak
                    tab_obj.create({
                        'tgl_trans': date_trans,
                        'jns_trans': 'TD',
                        'keterangan': 'Pajak Bunga Deposito',
                        'partner_id': partner_id,
                        'no_agt': no_agt,
                        'jenis_tabungan': jenis_tabungan,
                        'no_rekening': no_rekening,
                        'nama_rekening': nama_rekening,
                        'jml_tab': jml_pajak,
                        'balance_awal_view': balance_awal,
                        'balance_awal': balance_awal,
                        'debit': jml_pajak,
                        'balance_akhir_view': balance_akhir,
                        'balance_akhir': balance_akhir,
                        'code_trans': 'PJK',
                        'state': 'done',
                    })
                #buat journal move
                journal_id = settings_obj.journal_id.id
                mycomp = self._get_company_id()
                acc_anna = self.env['account.analytic.account'].search(
                    ['&', ('name', '=', '300 - Unit Simpan Pinjam'), ('company_id', '=', mycomp)],
                    limit=1)
                acc_item = []
                acc_line ={}
                acc_line = {'account_id': settings_obj.coa_depo_bebanjasa.id,
                            'name': 'Beban Bunga Deposito',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': jml_bunga,
                            'credit': 0}
                acc_item.append((0, 0, acc_line))
                acc_line = {'account_id': settings_obj.coa_depo_kliring_transfer.id,
                            'name': 'Bunga Deposito',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': rencana_bayar}
                acc_item.append((0, 0, acc_line))
                acc_line = {'account_id': settings_obj.coa_depo_pajak.id,
                            'name': 'Pajak Bunga Deposito',
                            'analytic_account_id': acc_anna.id,
                            'analytic_tag_ids': '',
                            'company_id': mycomp,
                            'debit': 0,
                            'credit': jml_pajak}
                acc_item.append((0, 0, acc_line))
                acc_setor = {}
                lstjr = self.get_last_journal()
                lstjr += 1
                counter = str(lstjr + 1)
                namaaccount = '%s/%s/%s' % ('KOPKARTRNS', tahun, counter)
                acc_setor = {'date': date_trans,
                             'journal_id': journal_id,
                             'company_id': mycomp,
                             'ref': 'Bunga Simpanan Berjangka',
                             'name': namaaccount}
                acc_setor['line_ids'] = acc_item
                buat_jurnal_setor = self.env['account.move'].create(acc_setor)
                buat_jurnal_setor.post()

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

    def get_last_journal(self):
        #mmsql = """SELECT count(name) FROM account_move;"""
        mmsql="""SELECT max(id) FROM account_move;"""
        self.env.cr.execute(mmsql,)
        res = self.env.cr.fetchone()[0]
        if res:
            return res
        else:
            return 0




