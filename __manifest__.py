# -*- coding: utf-8 -*-
{
    'name': "Yudha Simpan Pinjam",
    'summary': """
        Saving and loans: manage saving and manage loans in cooperative company""",
    'description': """
        saving and loan cooperative,
        saving,
        loan,
        loans,
        loan module,
        loans module
        loan in odoo,
        loans in odoo,
        saving module,
        saving and loan,
        cooperative,
        simpan,
        simpanan,
        simpan pinjam,
        simpan - pinjam,
        pinjaman,
        simpan pinjam koperasi,
        koperasi simpan pinjam,
        koperasi,
        koperasi simpan,
        koperasi pinjam,
        manage saving,
        manage loans,
        manage saving and loans,
    """,
    'author': "Albertus Restiyanto Pramayudha",
    'website': "https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',
    'application': True,
    'currency': 'EUR',
    'price': 156,

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'point_of_sale',
                'sale_management',
                'base_setup',
                'web',
                'portal',
                'purchase',
                'stock',
                'mrp',
                'purchase_requisition',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/core_simpan_pinjam/yudha_sequence_data.xml',
        'views/core_simpan_pinjam/yudha_menu.xml',
        'views/core_simpan_pinjam/yudha_product.xml',
        'views/core_simpan_pinjam/yudha_register_tabungan.xml',
        'views/core_simpan_pinjam/yudha_master_department.xml',
        'views/core_simpan_pinjam/yudha_master_golongan.xml',
        'views/core_simpan_pinjam/yudha_master_jenis_tabungan.xml',
        'views/core_simpan_pinjam/yudha_master_jenis_deposito.xml',
        'views/core_simpan_pinjam/yudha_rate_deposito.xml',
        'views/core_simpan_pinjam/yudha_rate_tabungan.xml',
        'views/core_simpan_pinjam/yudha_asal_perusahaan.xml',
        'views/core_simpan_pinjam/yudha_iuran_pokok.xml',
        'views/core_simpan_pinjam/yudha_iuran_wajib.xml',
        'views/core_simpan_pinjam/yudha_iuran_wajib_setor.xml',
        'views/core_simpan_pinjam/yudha_iuran_sukarela.xml',
        'views/core_simpan_pinjam/yudha_tabungan.xml',
        'views/core_simpan_pinjam/yudha_res_partner.xml',
        'views/core_simpan_pinjam/yudha_deposito.xml',
        'views/core_simpan_pinjam/yudha_validasi_harian.xml',
        'views/core_simpan_pinjam/yudha_validasi_sembako.xml',
        'views/core_simpan_pinjam/yudha_validasi_bulanan.xml',
        'views/core_simpan_pinjam/yudha_peminjaman_dana.xml',
        'views/core_simpan_pinjam/yudha_peminjaman_konsumtif.xml',
        'views/core_simpan_pinjam/yudha_peminjaman_syariah.xml',
        'views/core_simpan_pinjam/yudha_peminjaman_barang.xml',
        'views/core_simpan_pinjam/yudha_peminjaman_sembako.xml',
        'views/core_simpan_pinjam/yudha_account_payment.xml',
        'views/core_simpan_pinjam/yudha_settings.xml',
        'views/core_simpan_pinjam/yudha_laporan_harian.xml',
        'views/core_simpan_pinjam/yudha_laporan_bulanan.xml',
        'views/core_simpan_pinjam/yudha_laporan_detail_anggota.xml',
        'views/core_simpan_pinjam/yudha_laporan_deposito_transfer.xml',
        'reports/core_simpan_pinjam/yudha_buku_tabungan.xml',
        'reports/core_simpan_pinjam/yudha_buku_tabungan_validasi.xml',
        'reports/core_simpan_pinjam/yudha_jadwal_angsuran_dana.xml',
        'reports/core_simpan_pinjam/yudha_jadwal_angsuran_barang.xml',
        'reports/core_simpan_pinjam/yudha_jadwal_angsuran_syariah.xml',
        'reports/core_simpan_pinjam/yudha_jadwal_angsuran_konsumtif.xml',
        'reports/core_simpan_pinjam/yudha_kartu_pinjaman_dana.xml',
        'reports/core_simpan_pinjam/yudha_kartu_pinjaman_barang.xml',
        'reports/core_simpan_pinjam/yudha_kartu_pinjaman_konsumtif.xml',
        'reports/core_simpan_pinjam/yudha_kartu_pinjaman_syariah.xml',
        'data/core_simpan_pinjam/yudha_perhitungan_bunga_deposito.xml',
        'data/core_simpan_pinjam/yudha_perhitungan_bunga_tabungan.xml',

        'views/yudha_web_login/yudha_login_captcha.xml',
        'views/yudha_web_login/yudha_show_password.xml',
        'views/yudha_web_login/yudha_login_assets.xml',
        'views/yudha_web_login/yudha_login_image.xml',
        'views/yudha_web_login/yudha_res_config_login.xml',
        'views/yudha_web_login/yudha_login_security_settings.xml',
        'views/yudha_web_login/login_template/yudha_login_kanan.xml',
        'views/yudha_web_login/login_template/yudha_login_kiri.xml',
        'views/yudha_web_login/login_template/yudha_login_tengah.xml',
        'views/yudha_web_login/login_template/yudha_blocked_ip.xml',
        'views/yudha_web_login/login_template/yudha_country_blocked.xml',
        'views/yudha_web_login/login_template/yudha_no_proxy.xml',
        'views/yudha_web_login/login_template/yudha_username_blocked.xml',
        'security/yudha_web_login/ir.model.access.csv',
        'views/so_po_barcode/yudha_so_po_barcodes_purchase_view.xml',
        'views/so_po_barcode/yudha_so_po_barcodes_sales_view.xml',

        'views/multi_backdate/yudha_multi_backdate_stock_move.xml',
        'views/multi_backdate/yudha_multi_backdate_stock_picking.xml',

        'wizards/multi_backdate/yudha_multi_backdate_inventory_adjustment.xml',
        'wizards/multi_backdate/yudha_multi_backdate_wizards.xml',

        'views/multi_cancel/yudha_multi_cancel_mrp_view.xml',
        'views/multi_cancel/yudha_multi_cancel_remarks.xml',
        'views/multi_cancel/yudha_multi_cancel_stockpicking.xml',

        'views/product/product_template_views.xml',
        'views/product_date/yudha_product_date_view.xml',
        'views/product_approval/yudha_product_ecommerce_view.xml',
        'views/product_approval/yudha_product_product_views.xml',
        'views/product_approval/yudha_product_template_views.xml',
        'views/product_approval/yudha_stock_menu_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
}
