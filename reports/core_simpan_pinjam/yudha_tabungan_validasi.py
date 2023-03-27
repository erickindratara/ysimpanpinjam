# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

import time
from odoo import api, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools.float_utils import float_round as round


class yudha_rpt_tabungan_Validasi(models.AbstractModel):
    _name ='report.yudha_simpan_pinjam.tabungan_validasi_report'


    @api.model
    def _get_report_values(self, docids, data):
        model_id = data['model_id']
        value = []
        query = """SELECT *
                    	FROM yudha_tabungan as s_l
                    	WHERE s_l.id = %s"""
        value.append(model_id)
        self._cr.execute(query, value)
        record = self._cr.dictfetchall()
        return {
            'docs': record,
        }