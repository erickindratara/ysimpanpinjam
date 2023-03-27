# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
import time


class yudha_multi_backdate_rubahinfo(models.TransientModel):
    _name = "change.inventory.adjust"
    _description = "Change Inventory Adjustment"

    transfer_date6 = fields.Date('Inventory Date', required=True)
    transfer_remark6 = fields.Char('Remark', required=True)

    def Apply_Changes(self):
        myinv = self.env.context.get('default_inventory_id')
        yudha_multi_backdate_ids = self.env['stock.inventory'].browse(myinv)
        for allids in yudha_multi_backdate_ids:
            allids.write({'accounting_date': self.transfer_date6})
            allids.write({'transfer_date': self.transfer_date6})
            allids.write({'remark': self.transfer_remark6})
        mytest = yudha_multi_backdate_ids.action_validate2()
        if mytest ==True:
            for yudha_multi_backdate_ids1 in yudha_multi_backdate_ids:
                yudha_multi_backdate_ids1.write({'accounting_date': self.transfer_date6})
                for yudha_stock_inventory_ids2 in yudha_multi_backdate_ids1.move_ids:
                    yudha_stock_inventory_ids2.write({'date': yudha_multi_backdate_ids1.accounting_date,
                                                       'remark': self.transfer_remark6})

                    for yudha_multi_backdate_ids4 in yudha_stock_inventory_ids2.move_line_ids:
                        yudha_multi_backdate_ids4.write({'date': yudha_stock_inventory_ids2.date,
                                                           'remark': self.transfer_remark6})

                        yudha_accountmove = self.env['account.move'].create({'date': self.transfer_date6,
                                                                              'journal_id': yudha_stock_inventory_ids2.product_id.categ_id.property_stock_journal.id,
                                                                              'stock_move_id': yudha_stock_inventory_ids2.id})

                        yudha_accountmove.post()
        else:
            raise UserError(_('Validation Error'))
